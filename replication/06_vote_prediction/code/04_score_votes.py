#!/usr/bin/env python
"""Study V stage 4 (GPU): next-token YEA/NAY probabilities for the prompt table (PROTOCOL §3-5).

One forward pass per prompt; at the first response position we keep p(YEA first token), p(NAY first token), the summed probability of
case and space variants (diagnostic), and the top-1 token. Prompts are processed in resumable parts of PART rows; a part is written
atomically and then marked done, so an interrupted run restarts where it stopped. Memory (rebuild 2026-10-23): bf16 via
common/loader.py, per-process GPU cap and RAM guard from config/run.json, OOM stops; several shard processes may run at once (--shard).

  python 04_score_votes.py --model qwen --fixture                         # gate 1: token IDs and a decoded prompt
  python 04_score_votes.py --model qwen --smoke                           # gate 3: 5 roll calls x 20 members, run twice
  python 04_score_votes.py --model qwen --select pilot                    # abortion, main sample, main prompt
  python 04_score_votes.py --model qwen --select main | sensitivity | variants
"""
import argparse, json, os, sys, time
from pathlib import Path
import numpy as np, pandas as pd, torch

V = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(V.parent / "02_ideology_map" / "code"))
import map_common as dc  # noqa: E402

PART = 2000
ap = argparse.ArgumentParser()
ap.add_argument("--model", required=True, choices=list(dc.MODELS))
ap.add_argument("--select", choices=["pilot", "economic", "main", "sensitivity", "variants", "V1", "V2", "V3",
                                     "swap_abortion", "swap_economic", "sample_yf", "guns", "swap_guns"])
# guns / swap_guns (amendment A14, 2026-10-22): G2 gun votes, prompts from out/g2/ (YEA-first / NAY-first); other selections unchanged
# main = pilot + economic; swap_* = NAY-first half (A4); sample_yf = YEA-first main prompts on the sealed 25% roll-call sample that are not
# already scored in pilot/economic (A5 sample test; its NAY-first half is --select V2)
ap.add_argument("--fixture", action="store_true"); ap.add_argument("--smoke", action="store_true")
# batch 1 (2026-10-20, diag_padding.py): with the FP8 loader, batched scoring differed from single-prompt scoring by up to 0.33 in the
# YEA share (0.18 even without padding), and the single-prompt reading agreed with greedy generation. Batch 1 makes each prompt's result
# independent of which prompts share its batch. Larger batches remain available only for diagnostics.
ap.add_argument("--batch", type=int, default=dc.batch("v4"))
# Rebuild PLAN v0.2 §9.3 (2026-10-23): --shard i/n scores parts k with k % n == i, so several processes share one selection. Parts are
# fixed blocks of PART prompts of the full selection sorted by pid; at batch 1 every prompt is scored alone, so the files do not depend
# on n. The process that finds every part done writes the coverage check and run.json.
ap.add_argument("--shard", default=None, help="i/n")
a = ap.parse_args()
assert not a.shard or a.batch == 1, "sharding is only result-neutral at batch 1"

# Memory (amendment A1, 2026-10-20): the first pilot was stopped by host-RAM pressure while loading. Read only the rows and columns a
# run needs, require 5 GB free RAM before loading the model, and between parts wait (do not continue) while free RAM is below 2 GB.
COLS = ["pid", "key", "variant", "main_sample", "issue", "actual", "text"]
G2 = V / "out" / "g2"
if a.select in ("guns", "swap_guns"):                               # A14
    P = pd.read_parquet(G2 / ("prompts.parquet" if a.select == "guns" else "prompts_swap.parquet"), columns=COLS)
elif a.fixture or a.smoke:
    P = pd.read_parquet(V / "out" / "v3" / "prompts.parquet", columns=COLS, filters=[("variant", "==", "main"), ("main_sample", "==", True)])
elif a.select == "sample_yf":
    P = pd.read_parquet(V / "out" / "v3" / "prompts.parquet", columns=COLS, filters=[("variant", "==", "main"), ("main_sample", "==", True)])
    keys = set(pd.read_csv(V / "out" / "v3" / "variant_rollcalls.csv").key)
    done_pids = set()
    for s in ["pilot", "economic"]:
        for f in (V / "out" / "v4" / a.model / s).glob("part_*.parquet"):
            done_pids |= set(pd.read_parquet(f, columns=["pid"]).pid)
    P = P[P.key.isin(keys) & ~P.pid.isin(done_pids)]
elif a.select.startswith("swap_"):
    P = pd.read_parquet(V / "out" / "v3" / "prompts_swap.parquet", columns=COLS, filters=[("issue", "==", a.select.split("_")[1])])
    # NAY-first votes already scored as V2 (identical text, checked in v3b; deterministic batch-1 scoring) are not rescored
    v2 = set()
    for f in (V / "out" / "v4" / a.model / "V2").glob("part_*.parquet"):
        v2 |= set(pd.read_parquet(f, columns=["pid"]).pid.str.replace(r"\|V2$", "|swap", regex=True))
    P = P[~P.pid.isin(v2)]
else:
    flt = {"pilot": [("variant", "==", "main"), ("main_sample", "==", True), ("issue", "==", "abortion")],
           "economic": [("variant", "==", "main"), ("main_sample", "==", True), ("issue", "==", "economic")],
           "main": [("variant", "==", "main"), ("main_sample", "==", True)],
           "sensitivity": [("variant", "==", "main"), ("main_sample", "==", False)],
           "variants": [("variant", "!=", "main")],
           "V1": [("variant", "==", "V1")], "V2": [("variant", "==", "V2")], "V3": [("variant", "==", "V3")]}[a.select]
    P = pd.read_parquet(V / "out" / "v3" / "prompts.parquet", columns=COLS, filters=flt)
    if a.select in ("pilot", "economic"):                          # A7: votes already scored YEA-first in the sample test are not rescored
        done_s = set()
        for f in (V / "out" / "v4" / a.model / "sample_yf").glob("part_*.parquet"):
            done_s |= set(pd.read_parquet(f, columns=["pid"]).pid)
        P = P[~P.pid.isin(done_s)]
def select(P, s):
    if s == "pilot": return P[(P.variant == "main") & P.main_sample & (P.issue == "abortion")]
    if s == "economic": return P[(P.variant == "main") & P.main_sample & (P.issue == "economic")]
    if s == "main": return P[(P.variant == "main") & P.main_sample]
    if s == "sensitivity": return P[(P.variant == "main") & ~P.main_sample]
    if s == "variants": return P[P.variant != "main"]
    if s in ("V1", "V2", "V3"): return P[P.variant == s]
    if s.startswith("swap_") or s in ("sample_yf", "guns"): return P
    raise ValueError(s)

def token_ids(tok):
    ids = {}
    for w in ["YEA", "NAY"]:
        e = tok.encode(w, add_special_tokens=False)
        ids[w] = e[0]
        alts = set()
        for f in [w, " " + w, w.title(), " " + w.title(), w.lower(), " " + w.lower()]:
            alts.add(tok.encode(f, add_special_tokens=False)[0])
        ids[w + "_any"] = sorted(alts)
    return ids

def score(tok, model, texts, ids, batch):
    """returns DataFrame of p_yea, p_nay, p_yea_any, p_nay_any, top1_id, top1_p (same order as texts)"""
    chats = [dc.chat(tok, [{"role": "user", "content": t}]) for t in texts]
    lens = np.array([len(c) for c in chats]); order = np.argsort(lens)
    res = np.zeros((len(chats), 6)); b0 = 0; bs = batch
    ya, na = torch.tensor(ids["YEA_any"]), torch.tensor(ids["NAY_any"])
    while b0 < len(chats):
        idx = order[b0:b0 + bs]
        try:
            with torch.no_grad():
                enc = tok([chats[i] for i in idx], return_tensors="pt", padding=True, add_special_tokens=False).to("cuda")
                h = model.model(**enc).last_hidden_state[:, -1, :]
                pr = torch.softmax(model.lm_head(h).float(), -1).cpu()
        except torch.cuda.OutOfMemoryError as e:
            dc.oom_stop("v4 scoring", e)         # rebuild PLAN v0.2 §4.2: the batch is never lowered
        top = pr.max(-1)
        res[idx] = np.stack([pr[:, ids["YEA"]].numpy(), pr[:, ids["NAY"]].numpy(), pr[:, ya].sum(-1).numpy(),
                             pr[:, na].sum(-1).numpy(), top.indices.numpy(), top.values.numpy()], 1)
        b0 += len(idx)
    return pd.DataFrame(res, columns=["p_yea", "p_nay", "p_yea_any", "p_nay_any", "top1_id", "top1_p"]).astype(
        {"top1_id": int})

import gc
dc.ram_guard(need_gb=5.0)
tok, model = dc.load(a.model)
model.eval()
ids = token_ids(tok)
O = V / "out" / "v4" / a.model; O.mkdir(parents=True, exist_ok=True)
meta = dict(model=dc.MODELS[a.model], revision=getattr(model.config, "_commit_hash", None), token_ids=ids,
            decoded={k: tok.decode([ids[k]]) for k in ["YEA", "NAY"]}, torch=torch.__version__,
            prompts_sha256=json.load(open((G2 if a.select in ("guns", "swap_guns") else V / "out" / "v3") /
                                          ("summary_swap.json" if (a.select or "").startswith("swap_") else "summary.json")))["text_sha256"],
            gpu=torch.cuda.get_device_name(0))

if a.fixture:
    ex = P[P.variant == "main"].text.iloc[0]
    meta["example_chat"] = dc.chat(tok, [{"role": "user", "content": ex}])
    ok = ids["YEA"] != ids["NAY"] and "YEA".startswith(meta["decoded"]["YEA"].strip()) and "NAY".startswith(meta["decoded"]["NAY"].strip()) \
         and meta["decoded"]["YEA"].strip() != "" and meta["decoded"]["NAY"].strip() != ""
    meta["fixture_pass"] = bool(ok)
    dc.atomic_json(meta, O / "fixture.json"); print(json.dumps({k: v for k, v in meta.items() if k != "example_chat"}, indent=1))
    print(meta["example_chat"]); sys.exit(0 if ok else 1)

if a.smoke:
    s = P[(P.variant == "main") & P.main_sample]
    keys = s.drop_duplicates("key").sample(5, random_state=dc.seed_for("V-smoke") % 2**32).key
    s = s[s.key.isin(keys)].groupby("key").head(4)                    # 5 roll calls x 4 members = 20 prompts
    t0 = time.time(); r1 = score(tok, model, s.text.tolist(), ids, a.batch); t1 = time.time()
    r2 = score(tok, model, s.text.tolist(), ids, a.batch)
    pred1 = (r1.p_yea / (r1.p_yea + r1.p_nay) > 0.5); pred2 = (r2.p_yea / (r2.p_yea + r2.p_nay) > 0.5)
    # The first tokens of YEA and NAY are "Y" and "N" in all three tokenizers (fixture 2026-10-20). Check by greedy generation that
    # the model's actual answer is the word YEA or NAY and agrees with the first-token reading.
    gens = []
    for t in s.text:
        enc = tok([dc.chat(tok, [{"role": "user", "content": t}])], return_tensors="pt", add_special_tokens=False).to("cuda")
        with torch.no_grad():
            g = model.generate(**enc, max_new_tokens=4, do_sample=False, pad_token_id=tok.pad_token_id)
        gens.append(tok.decode(g[0, enc["input_ids"].shape[1]:], skip_special_tokens=True).strip())
    word = pd.Series(gens).str.upper().str.extract(r"^(YEA|NAY)")[0]
    out = dict(**meta, n=len(s), sec_per_prompt=round((t1 - t0) / len(s), 4), format_fail=int(((r1.p_yea + r1.p_nay) < 0.5).sum()),
               mass_median=float((r1.p_yea + r1.p_nay).median()), repeat_identical_predictions=bool((pred1 == pred2).all()),
               max_abs_diff_p=float((r1.p_yea - r2.p_yea).abs().max()), accuracy=float((pred1.astype(int).values == s.actual.values).mean()),
               top1=[tok.decode([int(i)]) for i in r1.top1_id.head(10)], generations=gens,
               generation_is_yea_or_nay=int(word.notna().sum()),
               generation_agrees_with_first_token=int((word.eq("YEA").values == pred1.values)[word.notna().values].sum()),
               ratio_where_disagree=[round(float(x), 4) for x in (r1.p_yea / (r1.p_yea + r1.p_nay))[(word.eq("YEA").values != pred1.values)]],
               batch1_vs_batched_max_abs_diff=float((score(tok, model, s.text.tolist(), ids, 1).p_yea - r1.p_yea).abs().max()),
               batch1_ratio_where_disagree=[round(float(x), 4) for x in (lambda r: r.p_yea / (r.p_yea + r.p_nay))(
                   score(tok, model, s.text.tolist(), ids, 1))[(word.eq("YEA").values != pred1.values)]])
    dc.atomic_json(out, O / ("smoke_guns.json" if a.select == "guns" else "smoke.json")); print(json.dumps({k: v for k, v in out.items() if k not in ("token_ids",)}, indent=1)); sys.exit(0)

S = select(P, a.select).sort_values("pid").reset_index(drop=True)
D = O / a.select; D.mkdir(exist_ok=True)
# Fixed partition (rebuild, fresh runs): part k = rows [k*PART, (k+1)*PART) of the sorted selection; done parts are skipped. The sealed
# FP8 runs resumed by vote id (A10) because their selections changed between runs; a fresh rebuild run has no such history.
n_all = len(S); n_parts = (n_all + PART - 1) // PART
si, sn = map(int, a.shard.split("/")) if a.shard else (0, 1)
mine = [k for k in range(n_parts) if k % sn == si and not (D / f"part_{k:04d}.done").exists()]
dc.log(a.model, a.select, n_all, "prompts in", n_parts, "parts; shard", f"{si}/{sn}", "scores", len(mine))
t_start = time.time()
for j, k in enumerate(mine):
    done = D / f"part_{k:04d}.done"
    chunk = S.iloc[k * PART:(k + 1) * PART]
    n_parts_mine = len(mine)
    if dc.free_ram_gb() < 2.0:
        dc.log(f"free RAM {dc.free_ram_gb():.1f} GB < 2 GB: waiting"); gc.collect(); torch.cuda.empty_cache(); dc.ram_guard(need_gb=3.0)
    r = score(tok, model, chunk.text.tolist(), ids, a.batch)
    r.insert(0, "pid", chunk.pid.values)
    tmp = D / f"part_{k:04d}.parquet.tmp"; r.to_parquet(tmp, index=False); os.replace(tmp, D / f"part_{k:04d}.parquet")
    done.write_text("ok")
    del r, chunk; gc.collect()
    el = time.time() - t_start; dc.log(f"part {j + 1}/{n_parts_mine} (file {k}) | {el / 60:.1f} min | free RAM {dc.free_ram_gb():.1f} GB")
if any(not (D / f"part_{k:04d}.done").exists() for k in range(n_parts)):
    dc.log("shard finished; other parts still running"); sys.exit(0)
# coverage check: every vote of the selection is in exactly one done part
got = pd.concat([pd.read_parquet(f.with_suffix(".parquet"), columns=["pid"]) for f in sorted(D.glob("part_*.done"))]).pid
full = select(P, a.select).pid
assert not got.duplicated().any() and set(got) == set(full), ("coverage", len(got), got.duplicated().sum(), len(set(full) - set(got)))
meta.update(select=a.select, n=n_all, parts=len(list(D.glob("part_*.done"))), finished=time.strftime("%Y-%m-%dT%H:%M:%S"),
            precision=dc._ld.CFG["precision"], batch=a.batch)
dc.atomic_json(meta, D / "run.json")
dc.log("done")
