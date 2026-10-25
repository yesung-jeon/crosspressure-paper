"""Study N [B] (PROTOCOL): for every analysis row (member-Congress), Kim's named persona (system) and each of Section 5's 16 single-axis
items with two answer orders (" Answer with Yes or No." / " Answer with No or Yes."), the full-softmax P(Yes), P(No) of the first answer
token (same definition as 11_stated_profiles.py yes_no). No steering, no projection.
Memory (global rule): RAM guard before loading (5 GB) and between parts (2 GB); per-process GPU cap (common/loader.py); OOM stops (rebuild);
parts of 200 rows written atomically with done markers and resumed by row id; coverage check at the end; one GPU process at a time.
  python 04_score_yes_no.py --model qwen --r2       # gate R2: Section 5 I4 (120 named members, "Yes or No") vs the sealed items.csv
  python 04_score_yes_no.py --model qwen --smoke    # 40 seeded analysis rows -> out/<m>/yesno_smoke/ (timing)
  python 04_score_yes_no.py --model qwen            # all 10,444 rows -> out/<m>/yesno/part_*.parquet"""
import argparse, gc, json, os, sys, time
import numpy as np, pandas as pd, torch
from named_common import dc, OUT, PART_ROWS, FMT, RAM_LOAD_GB, RAM_PART_GB, analysis_rows, items, want_yes, hbits, wait_ram

ap = argparse.ArgumentParser(); ap.add_argument("--model", required=True, choices=list(dc.MODELS))
ap.add_argument("--smoke", action="store_true"); ap.add_argument("--r2", action="store_true")
ap.add_argument("--batch", type=int, default=dc.batch("n2_yesno"))   # PROTOCOL_A1: batch 1 (config/run.json)
# Rebuild PLAN v0.2 §9.3: --shard i/n scores parts k with k % n == i (fixed blocks of PART_ROWS rows sorted by rid); result-neutral at batch 1
ap.add_argument("--shard", default=None, help="i/n")
a = ap.parse_args()
assert not a.shard or a.batch == 1, "sharding is only result-neutral at batch 1"
ITEMS = items(); D = OUT / a.model; D.mkdir(parents=True, exist_ok=True)

wait_ram(RAM_LOAD_GB)
tok, model = dc.load(a.model)
YES, NO = tok.encode("Yes", add_special_tokens=False), tok.encode("No", add_special_tokens=False)
assert len(YES) == 1 and len(NO) == 1 and YES != NO, (YES, NO)
YES, NO = YES[0], NO[0]
batch = a.batch


@torch.inference_mode()
def yes_no(prompts):
    """11_stated_profiles.py yes_no: last hidden state -> lm_head -> full softmax, P(Yes), P(No); length-sorted batches; OOM stops (rebuild)"""
    global batch
    lens = np.array([len(tok(p, add_special_tokens=False)["input_ids"]) for p in prompts]); order = np.argsort(lens)
    res = np.zeros((len(prompts), 2)); b0 = 0
    while b0 < len(prompts):
        idx = order[b0:b0 + batch]
        try:
            enc = tok([prompts[i] for i in idx], return_tensors="pt", padding=True, add_special_tokens=False).to("cuda")
            h = model.model(**enc).last_hidden_state[:, -1, :]
            p = torch.softmax(model.lm_head(h).float(), -1)
            res[idx] = torch.stack([p[:, YES], p[:, NO]], 1).cpu().numpy(); b0 += len(idx)
            del enc, h, p
        except torch.OutOfMemoryError as e:
            dc.oom_stop("n2_yesno", e)           # rebuild PLAN v0.2 §4.2: the batch is never lowered
    return res


def prompt(r, it, o):
    return dc.chat(tok, [{"role": "system", "content": dc.kim_persona(r["name"], r["chamber"], r["state"], int(r["year"]))},
                         {"role": "user", "content": it["q"] + FMT[o]}])


if a.r2:   # ---- gate R2: Section 5 I4 rows, "Yes or No" only, against the sealed s5 items.csv ----
    i4 = pd.read_csv(dc.OUT / "s5" / "i4_members.csv")
    cond = pd.read_csv(dc.OUT / a.model / "s5" / "conditions.csv"); cond = cond[cond["mode"] == "I4"]
    i4["base"] = "m" + i4.icpsr.astype(int).astype(str) + "c" + i4.congress.astype(int).astype(str)
    i4 = i4.merge(cond[["base", "cid", "profile"]], on="base", suffixes=("", "_c"), validate="one_to_one")
    assert len(i4) == 120 and (i4.profile == i4.profile_c).all()
    rows, ps = [], []
    for _, r in i4.iterrows():
        for it in ITEMS:
            rows.append(dict(cid=int(r.cid), item=it["id"], profile=r.profile, want=want_yes(it, r.profile))); ps.append(prompt(r, it, "yn"))
    P = yes_no(ps); new = pd.DataFrame(rows); new["p_yes"], new["p_no"] = P[:, 0], P[:, 1]
    old = pd.read_csv(dc.OUT / a.model / "s5" / "items.csv")
    j = new.merge(old, on=["cid", "item"], validate="one_to_one")
    assert len(j) == len(new)
    for s, (py, pn) in {"new": ("p_yes", "p_no"), "old": ("p_yes_raw", "p_no_raw")}.items():
        p = j[py] / (j[py] + j[pn]); j[f"H_{s}"] = hbits(p); j[f"C2_{s}"] = np.where(j.want, p, 1 - p)
    c = j.groupby(["cid", "profile"])[["H_new", "H_old", "C2_new", "C2_old"]].mean().reset_index()
    c["cross"] = c.profile.isin(["EL-ST", "ER-SP"]).astype(int)
    gap = lambda col: float(c[c.cross == 1][col].mean() - c[c.cross == 0][col].mean())
    out = {"model": a.model, "n_prompts": len(j), "max_abs_diff_C1a_by_condition": float((c.H_new - c.H_old).abs().max()),
           "max_abs_diff_C2_by_condition": float((c.C2_new - c.C2_old).abs().max()),
           "I4_cross_minus_aligned_C1a": {"new": gap("H_new"), "sealed": gap("H_old")},
           "I4_cross_minus_aligned_C2": {"new": gap("C2_new"), "sealed": gap("C2_old")},
           "max_abs_diff_p_yes": float((j.p_yes - j.p_yes_raw).abs().max()), "batch": batch}
    # PROTOCOL A1: the gate is the aggregate I4 contrasts; the per-condition rule (original PROTOCOL) is recorded, not gated
    out["pass_original_rule"] = bool(out["max_abs_diff_C1a_by_condition"] <= 0.02 and out["max_abs_diff_C2_by_condition"] <= 0.02
                                     and abs(gap("H_new") - gap("H_old")) <= 0.02 and abs(gap("C2_new") - gap("C2_old")) <= 0.02)
    out["pass"] = bool(abs(gap("H_new") - gap("H_old")) <= 0.02 and abs(gap("C2_new") - gap("C2_old")) <= 0.02)
    out["rule"] = "PROTOCOL_A1 aggregate"
    dc.atomic_json(out, D / "r2_check.json"); dc.log("R2", json.dumps(out)); sys.exit(0 if out["pass"] else 1)

# ---- main / smoke ----
R = analysis_rows(dc.OUT / a.model / "s3" / "temporal_member_scores.csv").sort_values("rid").reset_index(drop=True)
assert len(R) == 10444, len(R)
if a.smoke:
    R = R.sample(n=40, random_state=dc.seed_for("N-smoke") % 2**32).sort_values("rid").reset_index(drop=True)
P_DIR = D / ("yesno_smoke" if a.smoke else "yesno"); P_DIR.mkdir(parents=True, exist_ok=True)
# fixed partition (rebuild): part k = rows [k*PART_ROWS, (k+1)*PART_ROWS) of R sorted by rid; done parts are skipped
n_parts = int(np.ceil(len(R) / PART_ROWS))
si, sn = map(int, a.shard.split("/")) if a.shard else (0, 1)
mine = [k for k in range(n_parts) if k % sn == si and not (P_DIR / f"part_{k:04d}.done").exists()]
dc.log(f"{a.model}: {len(R)} rows in {n_parts} parts; shard {si}/{sn} scores {len(mine)}")
t_start = time.time(); n_prompts = 0; k0 = 0
for k in mine:
    blk = R.iloc[k * PART_ROWS:(k + 1) * PART_ROWS]; rows, ps = [], []
    for _, r in blk.iterrows():
        for it in ITEMS:
            for o in ("yn", "ny"):
                rows.append(dict(rid=r.rid, item=it["id"], axis=it["type"], order=o)); ps.append(prompt(r, it, o))
    t0 = time.time(); P = yes_no(ps); n_prompts += len(ps)
    df = pd.DataFrame(rows); df["p_yes"], df["p_no"] = P[:, 0], P[:, 1]
    f = P_DIR / f"part_{k0 + k:04d}.parquet"; tmp = f.with_name(f.name + ".tmp")
    df.to_parquet(tmp, index=False); os.replace(tmp, f); f.with_suffix(".done").touch()
    dc.log(f"part {k0 + k}: {len(blk)} rows, {len(ps)} prompts, {time.time() - t0:.0f}s ({(time.time() - t0) / len(ps):.4f} s/prompt), "
           f"batch {batch}, free RAM {dc.free_ram_gb():.1f} GB")
    del df, P, ps, rows; gc.collect(); torch.cuda.empty_cache(); wait_ram(RAM_PART_GB)
if any(not (P_DIR / f"part_{k:04d}.done").exists() for k in range(n_parts)):
    dc.log("shard finished; other parts still running"); sys.exit(0)
# coverage: every row x item x order exactly once among done parts
allp = pd.concat([pd.read_parquet(f.with_suffix(".parquet")) for f in sorted(P_DIR.glob("part_*.done"))], ignore_index=True)
key = allp.rid + "|" + allp["item"] + "|" + allp.order
assert not key.duplicated().any() and set(allp.rid) == set(R.rid) and len(allp) == len(R) * 32, "coverage check failed"
run = {"model": a.model, "rows": len(R), "prompts": len(allp), "seconds_this_run": round(time.time() - t_start), "prompts_this_run": n_prompts,
       "sec_per_prompt": round((time.time() - t_start) / max(n_prompts, 1), 4), "final_batch": batch,
       "mass_below_0.5": float(((allp.p_yes + allp.p_no) < 0.5).mean()), "token_ids": {"Yes": YES, "No": NO}}
dc.atomic_json(run, P_DIR / "run.json"); dc.log("done", json.dumps(run))
