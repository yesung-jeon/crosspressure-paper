#!/usr/bin/env python
"""Study M X4 (PLAN_X4.md), GPU part: conditional log-probability of each social clause after each economic clause, raw LM scoring
("{Cap(E)} and {S}", BOS only, no chat template, batch 1). -> out/x4/<model>/clause_logprob.csv (+ smoke/). Usage: python 05_x4_familiarity.py --model qwen [--smoke]"""
import argparse, json, sys
import numpy as np, pandas as pd, torch
import mech_common as xc
sys.path.insert(0, str(xc.K / "04_bundled_choices" / "code"))
import bundle_common as lc  # noqa: E402
import mech_decision_common as x5  # noqa: E402

ap = argparse.ArgumentParser(); ap.add_argument("--model", required=True, choices=["qwen", "llama"]); ap.add_argument("--smoke", action="store_true"); a = ap.parse_args()
od = xc.M / "out" / "x4" / a.model / ("smoke" if a.smoke else ""); od.mkdir(parents=True, exist_ok=True)
I = json.load(open(lc.jc.ITEMS, encoding="utf-8")); E, S = I["economic"], I["social"]
cap = lambda x: x[0].upper() + x[1:]
pairs = [(e, s) for e in x5.ECON for s in x5.SOC]
if a.smoke: pairs = pairs[:3]
tok, model = lc.load(a.model)

@torch.inference_mode()
def score(prefix, clause):
    """sum and mean log-prob of the clause tokens given the prefix (BOS + prefix + clause)"""
    bos = [tok.bos_token_id] if tok.bos_token_id is not None else []
    p = tok(prefix, add_special_tokens=False)["input_ids"]; full = tok(prefix + clause, add_special_tokens=False)["input_ids"]
    assert full[:len(p)] == p, "prefix tokenization changed at the boundary"
    ids = torch.tensor([bos + full], device="cuda"); out = model(ids).logits[0].float().log_softmax(-1)
    start = len(bos) + len(p); tgt = ids[0, start:]
    lp = out[start - 1:-1].gather(1, tgt[:, None])[:, 0]
    return float(lp.sum()), float(lp.mean()), int(len(tgt))

rows = []
for rep in ((0, 1) if a.smoke else (0,)):
    for e, s in pairs:
        for es in ("L", "R"):
            for ss in ("P", "T"):
                tot, mean, n = score(f"{cap(E[e][es])} and", " " + S[s][ss])   # smoke fix: the space goes with the clause (tokenizer boundary)
                rows.append(dict(rep=rep, econ=e, soc=s, e_side=es, s_side=ss, lp_sum=tot, lp_mean=mean, n_tok=n))
D = pd.DataFrame(rows); lc.atomic_csv(D, od / "clause_logprob.csv")
if a.smoke:
    w = D.pivot_table(index=["econ", "soc", "e_side", "s_side"], columns="rep", values="lp_sum"); print("smoke determinism max diff", float((w[0] - w[1]).abs().max()))
lc.log(f"x4 {a.model}: {len(D)} scores")
