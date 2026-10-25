#!/usr/bin/env python
"""Layer stability gate (rebuild PLAN v0.2 §6.3): the layer rule is run twice from scratch (s1 -> s2 generation -> judge -> rule), once
into 02_ideology_map/out and once into 02_ideology_map/out_layercheck, with the same configuration. Both runs must choose the same
common layer for every model, and the s1 differences must be identical; otherwise the pipeline stops before the map is projected.
-> 16_supplementary_checks/layercheck/layer_check.json"""
import json, sys
from pathlib import Path
import torch

R = Path(__file__).resolve().parents[2]; D = R / "02_ideology_map"
res = {}
for m in ("qwen", "llama"):
    a, b = (json.load(open(D / o / m / "rule.json", encoding="utf-8")) for o in ("out", "out_layercheck"))
    da, db = (torch.load(D / o / m / "s1" / "diffs_all.pt", weights_only=False)["diffs"] for o in ("out", "out_layercheck"))
    same_diffs = all(bool(torch.equal(da[k], db[k])) for k in ("economic", "social"))
    res[m] = {"layer_run1": a["common_layer"], "layer_run2": b["common_layer"], "same_layer": a["common_layer"] == b["common_layer"],
              "s1_diffs_identical": same_diffs, "rank_sum_identical": a["rank_sum"] == b["rank_sum"]}
res["pass"] = all(res[m]["same_layer"] and res[m]["s1_diffs_identical"] and res[m]["rank_sum_identical"] for m in ("qwen", "llama"))
json.dump(res, open(Path(__file__).parent / "layer_check.json", "w"), indent=1)
print(json.dumps(res))
sys.exit(0 if res["pass"] else 1)
