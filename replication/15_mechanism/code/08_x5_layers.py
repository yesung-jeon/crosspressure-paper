#!/usr/bin/env python
"""Study M X5 stage B (PLAN_X5 3), GPU: Study L's 20 personas x 108 bundled items x 2 orders, NONE (W = 0), saving every layer's float32
logit-lens A - B margin (steer_core.lens_run). Uses Study L / F helpers by import; sealed code is not edited.
Memory: GPU cap 80% and RAM guard (bundle_common.load), OOM batch halving (lens_run), parts of 5 personas with resumable files, one model per process.
-> out/x5/<model>/part_XX.csv.gz (+ smoke/). Usage: python 08_x5_layers.py --model qwen [--smoke]"""
import argparse, sys
import numpy as np, pandas as pd, torch
import mech_common as xc
sys.path.insert(0, str(xc.K / "04_bundled_choices" / "code"))
import bundle_common as lc  # noqa: E402

ap = argparse.ArgumentParser(); ap.add_argument("--model", required=True, choices=["qwen", "llama"]); ap.add_argument("--smoke", action="store_true")
ap.add_argument("--batch", type=int, default=lc.fc._ld.batch("m_x5_layers"))   # A1 (2026-10-18): stage B runs at --batch 1 -> out/x5/<model>/b1/
a = ap.parse_args()
od = xc.M / "out" / "x5" / a.model / ("b1" if a.batch == 1 else "") / ("smoke" if a.smoke else ""); od.mkdir(parents=True, exist_ok=True)
P = lc.personas("confirm"); D_, R_ = [p for p in P if p["party"] == "Democrat"], [p for p in P if p["party"] == "Republican"]
parts = [D_[i:i + 5] for i in (0, 5)] + [R_[i:i + 5] for i in (0, 5)]
bundles, _ = lc.items(); ITEMS = bundles
if a.smoke: parts = [[D_[0]]]; ITEMS = [b for b in bundles if b["econ"] == "health"]
todo = [i for i in range(len(parts)) if not (od / f"part_{i:02d}.csv.gz").exists()]
if not todo: lc.log(f"x5 {a.model}: all parts done"); sys.exit()
tok, model = lc.load(a.model); N = model.config.num_hidden_layers; L = lc.layer(a.model); d = model.config.hidden_size
lc.log(f"x5 {a.model}: layers {N}, steer layer {L}, items {len(ITEMS)}, parts todo {todo}")
with lc.Steer(model, L) as steer:
    for pi in todo:
        lc.fc.ram_guard(); rows, texts = [], []
        for p in parts[pi]:
            for b in ITEMS:
                for order in (0, 1):
                    A, Bp = (b["pkgL"], b["pkgR"]) if order == 0 else (b["pkgR"], b["pkgL"])
                    rows.append(dict(pid=p["pid"], party=p["party"], topic=b["topic"], family=b["family"], order=order))
                    texts.append(lc.chat(tok, lc.fc.choice_msgs(p["system"], A, Bp)))
        M, PA, PB = lc.lens_run(tok, model, steer, texts, torch.zeros(len(texts), d), batch=a.batch)
        D = pd.DataFrame(rows); D["pA"], D["pB"], D["m_final"] = PA, PB, M[:, -1]
        D["DL"] = [lc.decision_layer(m) for m in M]
        D = pd.concat([D, pd.DataFrame(M, columns=[f"m{l + 1:02d}" for l in range(N)])], axis=1)
        lc.atomic_csv(D, od / f"part_{pi:02d}.csv.gz"); lc.log(f"x5 {a.model} part {pi}: {len(D)} prompts, GPU peak {torch.cuda.max_memory_allocated() / 2**30:.1f} GB")
lc.log(f"x5 {a.model} complete")
