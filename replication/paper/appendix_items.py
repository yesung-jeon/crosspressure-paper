#!/usr/bin/env python
"""Write the item lists printed in Appendix A.6 (paper/tables/items_profiles.md, items_packages.md) from the package's item files,
so the appendix quotes the exact wording the models saw. Sources: 01_rollcall_scales/issue_data/cp3_items.json (stated profiles; the
sixteen single-issue items are also the named-member questions), 03_steering_tools/items_j.json (policy packages; the topic excluded
from the package task is read from 03_steering_tools/code/steer_separation.py EXCL_SOC).
Usage: python paper/appendix_items.py"""
import json, re
from pathlib import Path

P = Path(__file__).resolve().parent; R = P.parent
T = P / "tables"; T.mkdir(exist_ok=True)

items = json.load(open(R / "01_rollcall_scales/issue_data/cp3_items.json", encoding="utf-8"))["items"]
GROUPS = [("econ_only", "Economic only"), ("soc_only", "Social only"), ("concordant_LP", "Aligned, liberal on both"),
          ("concordant_RT", "Aligned, conservative on both"), ("cross_LT", "Crossed, economically liberal and socially conservative"),
          ("cross_RP", "Crossed, economically conservative and socially liberal")]
out = ["| Type | Item |", "|---|---|"]
for key, label in GROUPS:
    for it in (i for i in items if i["type"] == key):
        out.append(f"| {label} | {it['q']} |")
(T / "items_profiles.md").write_text("\n".join(out) + "\n", encoding="utf-8")

J = json.load(open(R / "03_steering_tools/items_j.json", encoding="utf-8"))
src = (R / "03_steering_tools/code/steer_separation.py").read_text(encoding="utf-8")
excl = json.loads(re.search(r"EXCL_SOC\s*=\s*(\[.*?\])", src).group(1).replace("'", '"'))
out = ["| Topic | Liberal or progressive position | Conservative or traditional position |", "|---|---|---|"]
for k, v in J["economic"].items():
    out.append(f"| Economic: {k} | {v['L']} | {v['R']} |")
for k, v in J["social"].items():
    if k in excl: continue
    out.append(f"| Social: {k} | {v['P']} | {v['T']} |")
(T / "items_packages.md").write_text("\n".join(out) + "\n", encoding="utf-8")
print("items_profiles.md, items_packages.md written")
