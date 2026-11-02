#!/usr/bin/env python
"""Continuous-scale scoring. Same rows, personas and texts as Study N and W1; only the answer instruction
changes to a 1-7 (named members) or 1-9 (votes) scale in two directions. One batch-1 forward pass per prompt on the sealed path
(model.model -> last_hidden_state[:, -1] -> lm_head -> full softmax); saves the probability of each digit token.
  python score_scale.py --model qwen --smoke          # 50 + 50 prompts twice: repeat bitwise, digit mass, greedy first token, timing
  python score_scale.py --model qwen --shard 0/4      # both tasks -> ../out/{named,votes}/<m>/part_*.parquet"""
import argparse, gc, json, os, sys, time
from pathlib import Path
import numpy as np, pandas as pd, torch

H = Path(__file__).resolve().parents[1]; REP = H.parent; V = REP / "10_vote_prediction"
sys.path.insert(0, str(REP / "15_named_member_uncertainty" / "code"))
from named_common import dc, analysis_rows, items  # noqa: E402

PART = 2000
SCALE7 = {"asc": " Answer with a single number from 1 to 7, where 1 means definitely no and 7 means definitely yes.",
          "desc": " Answer with a single number from 1 to 7, where 1 means definitely yes and 7 means definitely no."}
SCALE9 = {"asc": "Answer with a single number from 1 to 9, where 1 means you certainly vote NAY and 9 means you certainly vote YEA.",
          "desc": "Answer with a single number from 1 to 9, where 1 means you certainly vote YEA and 9 means you certainly vote NAY."}
LAST = "Respond with exactly one word: YEA or NAY."
# named9: the named-member questions on the vote task's 1-9 scale
SCALE9N = {"asc": " Answer with a single number from 1 to 9, where 1 means definitely no and 9 means definitely yes.",
           "desc": " Answer with a single number from 1 to 9, where 1 means definitely yes and 9 means definitely no."}
ap = argparse.ArgumentParser(); ap.add_argument("--model", required=True, choices=["qwen", "llama"])
ap.add_argument("--smoke", action="store_true"); ap.add_argument("--shard", default="0/1")
ap.add_argument("--tasks", default="named,votes", help="named,votes = the sealed 10-29 run; named9 = the 11-01 amendment"); a = ap.parse_args()


def named_table(tok, scale=None):
    scale = scale or SCALE7
    R = analysis_rows(dc.OUT / a.model / "s3" / "temporal_member_scores.csv").sort_values("rid").reset_index(drop=True)
    assert len(R) == 10444
    rows = []
    for r in R.itertuples():
        sysmsg = dc.kim_persona(r.name, r.chamber, r.state, int(r.year))
        for it in items():
            for o in ("asc", "desc"):
                rows.append((f"{r.rid}|{it['id']}|{o}", r.rid, it["id"], o, sysmsg, it["q"] + scale[o]))
    return pd.DataFrame(rows, columns=["key", "rid", "item", "order", "sys", "user"])


def votes_table():
    c = ["pid", "issue", "text"]
    y = pd.read_parquet(V / "out" / "v3" / "prompts.parquet", columns=c + ["variant", "main_sample"],
                        filters=[("variant", "==", "main"), ("main_sample", "==", True)])[c]
    g = pd.read_parquet(V / "out" / "g2" / "prompts.parquet", columns=c)
    P = pd.concat([y, g], ignore_index=True); assert len(P) == 102285 + 11934 and not P.pid.duplicated().any()
    assert P.text.str.endswith(LAST).all(), "unexpected last line"
    rows = []
    for r in P.itertuples():
        for o in ("asc", "desc"):
            rows.append((f"{r.pid}|{o}", r.pid, r.issue, o, None, r.text[: -len(LAST)] + SCALE9[o]))
    return pd.DataFrame(rows, columns=["key", "pid", "issue", "order", "sys", "user"]).sort_values("key").reset_index(drop=True)


# Amendment A1: the first smoke showed Llama opening with prose ("I would rate...",
# "As Representative ..."; digit mass median 0.08 / 0.02, format failure 100%) while Qwen answered with a digit. Both models therefore
# get the same assistant prefill "Answer: " after the generation prompt, and each digit's probability is the sum over its bare and
# space-prefixed single-token forms (" 7" and "7"), whichever exist in the tokenizer.
PREFILL = "Answer: "   # A1b: trailing space; both tokenizers split " 7" into " " + "7", so the digit is the next token


def chat(tok, s, u):
    msgs = ([{"role": "system", "content": s}] if s else []) + [{"role": "user", "content": u}]
    return dc.chat(tok, msgs) + PREFILL


def digit_ids(tok, n):
    ids = []
    for d in range(1, n + 1):
        v = sorted({e[0] for e in (tok.encode(str(d), add_special_tokens=False), tok.encode(" " + str(d), add_special_tokens=False)) if len(e) == 1})
        assert v, d; ids.append(v)
    flat = [i for v in ids for i in v]; assert len(set(flat)) == len(flat); return ids


@torch.inference_mode()
def score(tok, model, texts, ids):
    out = np.zeros((len(texts), len(ids)))
    for i, t in enumerate(texts):
        enc = tok([t], return_tensors="pt", padding=True, add_special_tokens=False).to("cuda")
        try:
            h = model.model(**enc).last_hidden_state[:, -1, :]; p = torch.softmax(model.lm_head(h).float(), -1)
        except torch.cuda.OutOfMemoryError as e:
            dc.oom_stop("scale scoring", e)
        out[i] = [float(p[0, v].sum()) for v in ids]
    return out


dc.ram_guard(need_gb=5.0)
tok, model = dc.load(a.model); model.eval()
BUILD = {"named": lambda: (named_table(tok), 7), "votes": lambda: (votes_table(), 9), "named9": lambda: (named_table(tok, SCALE9N), 9)}
TASKS = {t: BUILD[t]() for t in a.tasks.split(",")}
IDS = {t: digit_ids(tok, n) for t, (_, n) in TASKS.items()}

if a.smoke:
    out = dict(model=dc.MODELS[a.model], digit_ids={t: v for t, v in IDS.items()})
    for t, (T, n) in TASKS.items():
        s = T.sample(50, random_state=3); texts = [chat(tok, r.sys, r.user) for r in s.itertuples()]
        torch.cuda.reset_peak_memory_stats(); t0 = time.time(); P1 = score(tok, model, texts, IDS[t]); dt = (time.time() - t0) / len(texts)
        P2 = score(tok, model, texts, IDS[t]); mass = P1.sum(1)
        firsts = []
        for x in texts[:20]:
            enc = tok([x], return_tensors="pt", add_special_tokens=False).to("cuda")
            with torch.no_grad():
                g = model.generate(**enc, max_new_tokens=3, do_sample=False, pad_token_id=tok.pad_token_id)
            firsts.append(tok.decode(g[0, enc["input_ids"].shape[1]:], skip_special_tokens=True))
        out[t] = dict(sec_per_prompt=round(dt, 4), peak_gpu_gb=round(torch.cuda.max_memory_allocated() / 2**30, 2), repeat_bitwise=bool((P1 == P2).all()),
                      mass_median=float(np.median(mass)), format_fail_share=float((mass < 0.5).mean()),
                      greedy_starts_with_digit=float(np.mean([f.strip()[:1].isdigit() for f in firsts])), greedy_examples=firsts[:8],
                      example_prompt=texts[0])
    dc.atomic_json(out, H / "out" / f"smoke_{a.model}.json" if a.tasks == "named,votes" else H / "protocol" / f"smoke_named9_{a.model}.json")
    print(json.dumps({t: {k: v for k, v in out[t].items() if k != "example_prompt"} for t in TASKS}, indent=1, ensure_ascii=False))
    ok = all(out[t]["repeat_bitwise"] and out[t]["mass_median"] >= 0.9 and out[t]["format_fail_share"] < 0.05 and out[t]["greedy_starts_with_digit"] >= 0.95 for t in TASKS)
    sys.exit(0 if ok else 1)

si, sn = map(int, a.shard.split("/"))
for t, (T, n) in TASKS.items():
    D = H / "out" / t / a.model; D.mkdir(parents=True, exist_ok=True)
    n_parts = (len(T) + PART - 1) // PART
    mine = [k for k in range(n_parts) if k % sn == si and not (D / f"part_{k:04d}.done").exists()]
    dc.log(a.model, t, len(T), "prompts in", n_parts, "parts; shard", a.shard, "scores", len(mine))
    t_start = time.time()
    for j, k in enumerate(mine):
        if dc.free_ram_gb() < 2.0:
            gc.collect(); torch.cuda.empty_cache(); dc.ram_guard(need_gb=3.0)
        ch = T.iloc[k * PART:(k + 1) * PART]
        P = score(tok, model, [chat(tok, r.sys, r.user) for r in ch.itertuples()], IDS[t])
        df = ch.drop(columns=["sys", "user"]).reset_index(drop=True)
        for d in range(n): df[f"p{d + 1}"] = P[:, d]
        tmp = D / f"part_{k:04d}.parquet.tmp"; df.to_parquet(tmp, index=False); os.replace(tmp, D / f"part_{k:04d}.parquet")
        (D / f"part_{k:04d}.done").write_text("ok")
        dc.log(f"{a.model} {t} shard {a.shard} part {j + 1}/{len(mine)} (file {k}) | median mass {np.median(P.sum(1)):.3f} | {(time.time() - t_start) / 60:.1f} min")
        del P, df; gc.collect()
    if all((D / f"part_{k:04d}.done").exists() for k in range(n_parts)):
        got = pd.concat([pd.read_parquet(D / f"part_{k:04d}.parquet", columns=["key"]) for k in range(n_parts)]).key
        assert not got.duplicated().any() and set(got) == set(T.key), f"coverage {t}"
        dc.atomic_json(dict(model=dc.MODELS[a.model], task=t, n=len(T), digit_ids=IDS[t], finished=time.strftime("%Y-%m-%dT%H:%M:%S")), D / "run.json")
        dc.log(a.model, t, "all parts done")
