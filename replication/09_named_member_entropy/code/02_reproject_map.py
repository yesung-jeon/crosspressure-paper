"""Study N [A] (PROTOCOL R1): re-project the paper's map with Kim's congress_map/03_project_legislators.py run unchanged, exactly as
Study D 05_project_members.py --which main does (FP8 patch, sealed vectors.pt and layer, --batch 64, all 21,288 member-Congress rows), into
out/mapout/<m>/s3/ (sealed Study D files are read, never written). The sealed rule.json is copied beside it so 06_vote_vs_map.py can be
rerun on the new map (03_compare_map.py).
Usage: python 02_reproject_map.py --model qwen [--smoke]   (smoke: 40 seeded rows, as 05_project_members.py --smoke, into out/mapout_smoke/)"""
import argparse, runpy, shutil, sys
import pandas as pd
from named_common import dc, MAPOUT, OUT, RAM_LOAD_GB, wait_ram

ap = argparse.ArgumentParser(); ap.add_argument("--model", required=True, choices=list(dc.MODELS)); ap.add_argument("--smoke", action="store_true")
a = ap.parse_args()
root = OUT / "mapout_smoke" if a.smoke else MAPOUT
out = root / a.model / "s3"; out.mkdir(parents=True, exist_ok=True)
if (out / "temporal_member_scores.csv").exists():
    dc.log("map done, skipped"); sys.exit(0)
src = dc.OUT / a.model
shutil.copy2(src / "rule.json", root / a.model / "rule.json")
vec = src / "vectors.pt"; assert vec.exists()
voteview = dc.MEMBERS
if a.smoke:                                     # same subset rule as 05_project_members.py --smoke (40 seeded rows)
    m = pd.read_csv(dc.MEMBERS, low_memory=False)
    m = m[m.congress.between(80, 118) & m.chamber.isin(["House", "Senate"]) & m.nominate_dim1.notna()].drop_duplicates(["congress", "icpsr"])
    m = m.sample(n=40, random_state=dc.seed_for("D-B2") % 2**32)
    voteview = out / "members_subset.csv"; m.to_csv(voteview, index=False)
wait_ram(RAM_LOAD_GB)
dc.patch_from_pretrained()                      # bf16, pinned revision, GPU cap (as 05_project_members.py; rebuild PLAN v0.2 §4.1)
sys.argv = ["03_project_legislators.py", "--repo_root", str(dc.REPO), "--model", dc.MODELS[a.model], "--vectors", str(vec),
            "--voteview", str(voteview), "--out", str(out), "--batch", str(dc.batch("s3_project"))]
runpy.run_path(str(dc.CMAP / "03_project_legislators.py"), run_name="__main__")
dc.log("map written", out)
