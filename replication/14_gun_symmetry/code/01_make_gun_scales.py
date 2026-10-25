#!/usr/bin/env python
"""Gun version of the roll-call scales (rebuild PROTOCOL_GUNSYM, 2026-10-24). Copy of 01_rollcall_scales/out/data/issue_scales.csv in
which the social rows (issue = "abortion") are replaced by the G0 gun score (passing Congress x chamber cells; higher = more votes against
gun regulation = traditional side, as the abortion scale). Economic rows are unchanged. Scripts that read ISSUE_SCALES then run unchanged
on guns (label "abortion" = social scale = guns). -> 14_gun_symmetry/out/issue_scales_guns.csv, SOCIAL_SCALE.txt"""
from pathlib import Path
import pandas as pd

R = Path(__file__).resolve().parents[2]; O = Path(__file__).resolve().parents[1] / "out"; O.mkdir(exist_ok=True)   # file is in code/
sc = pd.read_csv(R / "01_rollcall_scales" / "out" / "data" / "issue_scales.csv")
g = pd.read_csv(R / "05_gun_scale" / "out" / "g0" / "gun_scales.csv")
soc = g.rename(columns={"gun_score": "rc_score"}).assign(issue="abortion", rc_share=float("nan"))[sc.columns]
out = pd.concat([sc[sc.issue != "abortion"], soc], ignore_index=True)
assert not out.duplicated(["congress", "chamber", "issue", "icpsr"]).any()
out.to_csv(O / "issue_scales_guns.csv", index=False)
(O / "SOCIAL_SCALE.txt").write_text("issue_scales_guns.csv: rows labelled 'abortion' hold the G0 gun score (social scale = guns), "
                                     f"{soc[['congress', 'chamber']].drop_duplicates().shape[0]} Congress x chamber cells, {len(soc)} member rows.\n")
print("gun scale rows", len(soc), "cells", soc[["congress", "chamber"]].drop_duplicates().shape[0])
