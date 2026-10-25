#!/usr/bin/env python
"""Single entry point of the replication package (rebuild PLAN v0.2, 2026-10-23; Rhee replication-package rules).

  python run_pipeline.py --path A     full rerun from raw data and the public models (GPU; H200 settings in config/run.json)
  python run_pipeline.py --path B     every CPU step from the shipped GPU outputs (no GPU)
  python run_pipeline.py --path A --until map.s3.qwen    run only the steps needed for one target
  python run_pipeline.py --list       print the step graph

Every step is one command with declared dependencies. A step runs when its dependencies are done; GPU steps share the card (config
"gpu_processes"), CPU steps share the cores (config "cpu_processes"). Each step leaves logs/pipeline/<step>.log and a done marker; a
rerun skips done steps, so an interrupted run resumes. The first failed step stops the run (running steps finish, nothing new starts).
run.json records every step's start, end, seconds, exit code and the configuration. Batch-1 GPU steps are split into shards
(--shard i/n), which does not change their outputs. Path B skips GPU steps and requires their shipped outputs.

Step names are <topic>.<step>[.<model>]; the topic names the folder: scales 01, map 02 (layer check map.lc), bundles 04, gunscale 05,
votes 06, uncertainty 07, warning 08, named 09, history 10, nominate 11, speech 12 (speech.d = state lean), fill 13, gunsym 14,
mechanism 15, checks 16. (Before 2026-10-24 the prefixes were study letters B, D, L, G, V, W1U, EW, N, T, NOM, SD, GF, SYM, M, post.)
"""
import argparse, json, os, platform, shlex, subprocess, sys, time
from pathlib import Path

R = Path(__file__).resolve().parent
CFG = json.load(open(R / "config" / "run.json", encoding="utf-8"))
M = list(CFG["models"])
RSCRIPT = os.environ.get("RSCRIPT", "Rscript")
LOGS = R / "logs" / "pipeline"
STEPS = {}


def step(name, cmd, cwd=".", deps=(), gpu=False, shards=1, env=None, path_b=True):
    """path_b=False: a CPU step inside a GPU chain whose inputs are not shipped (layer rule, layer check); Path B skips it like a GPU step.
    GPU memory budget (config gpu_gb): batch-1 scoring steps (shards > 1, or --batch 1 / single-sequence scoring) reserve 'light' GB,
    batched and generation steps 'heavy' GB; a GPU step starts only while the reserved total stays within gpu_gb.total. The budget sets
    the per-process cap (GPU_GB) and never changes outputs."""
    assert name not in STEPS, name
    light = gpu and (shards > 1 or any(k in name for k in ("X5_layers", "X4_familiarity", "named.R2")))
    STEPS[name] = dict(name=name, cmd=cmd, cwd=cwd, deps=list(deps), gpu=gpu, shards=shards, env=env or {}, path_b=path_b and not gpu,
                       gb=(CFG["gpu_gb"]["light"] if light else CFG["gpu_gb"]["heavy"]) if gpu else 0)


D, L, V, G, N, T = "02_ideology_map/code", "04_bundled_choices/code", "06_vote_prediction/code", "05_gun_scale/code", "09_named_member_entropy", "10_polarization_history/code"
LC = {"STUDYD_OUT": str(R / "02_ideology_map" / "out_layercheck")}
SH = CFG.get("shards", {})

# ---- 0-1 raw data and roll-call scales ----
step("fetch", "python data/fetch_data.py")
step("scales.issue_scales", "python 01_build_scales.py", "01_rollcall_scales/code", ["fetch"])
# ---- 2 directions, layer rule (twice: layer stability gate), map ----
for m in M:
    for pre, env in (("map", None), ("map.lc", LC)):
        step(f"{pre}.s1.{m}", f"python 01_extract_directions.py --model {m}", D, ["fetch"], gpu=True, env=env)
        step(f"{pre}.s2gen.{m}", f"python 02_steer_layers.py --model {m}", D, [f"{pre}.s1.{m}"], gpu=True, env=env)
        step(f"{pre}.s2judge.{m}", f"python 03_judge_steering.py --models {m}", D, [f"{pre}.s2gen.{m}"], gpu=True, env=env)
        step(f"{pre}.s2rule.{m}", f"python 04_select_layer.py --model {m}", D, [f"{pre}.s2judge.{m}"], env=env, path_b=False)
step("map.layercheck", "python 16_supplementary_checks/layercheck/layer_check.py", ".", [f"{p}.s2rule.{m}" for p in ("map", "map.lc") for m in M], path_b=False)
for m in M:
    step(f"map.s3.{m}", f"python 05_project_members.py --model {m} --which main", D, [f"map.s2rule.{m}", "map.layercheck"], gpu=True)
S3 = [f"map.s3.{m}" for m in M]
# ---- 3-4 shared definitions and Sections 4 (map) ----
step("map.s4", "python 06_vote_vs_map.py", D, S3 + ["scales.issue_scales"])
step("map.s4b_select", "python 07a_reselect_deepest.py", D, S3 + ["scales.issue_scales"])
step("map.s4c_select", "python 07b_reselect_by_votes.py", D, ["map.s4b_select"])
step("map.selection_report", "python tools/check_selection.py", ".", ["map.s4b_select", "map.s4c_select"])
step("map.s4c_positions", "python 08b_place_by_votes.py", D, ["map.s4"])
step("map.s4d", "python 09_within_party_by_era.py", D, S3 + ["scales.issue_scales"])
step("checks.benchmark", "python 16_supplementary_checks/benchmark/benchmark_recall.py", ".", ["map.s4"])
step("checks.members_by_era", "python 16_supplementary_checks/members_by_era/members_by_era.py", ".", ["map.s4", "map.s4c_positions"])
step("checks.noise_benchmark", "python 16_supplementary_checks/noise_benchmark/noise_benchmark.py", ".", ["checks.benchmark"])   # council 2026-10-25 B2
# ---- 5 stated profiles (Section 5) ----
step("map.s5_select", "python 10_select_profiles.py", D, S3, path_b=False)   # input of the GPU step s5_inject; Path B keeps the shipped selection
for m in M:
    step(f"map.s5.{m}", f"python 11_stated_profiles.py --model {m}", D, ["map.s5_select", f"map.s2rule.{m}"], gpu=True)
step("map.s5_analyze", "python 12_analyze_profiles.py", D, [f"map.s5.{m}" for m in M])
# ---- 6 bundled choices (Section 6) ----
for m in M:
    step(f"bundles.l0.{m}", f"python 01_calibrate_norms.py --model {m}", L, [f"map.s2rule.{m}", "map.layercheck"], gpu=True)
    step(f"bundles.l1.{m}", f"python 02_score_bundles.py --model {m}", L, [f"bundles.l0.{m}"], gpu=True)
    step(f"bundles.l2.{m}", f"python 03_analyze_bundles.py --model {m}", L, [f"bundles.l1.{m}"])
step("checks.no_persona", "python 16_supplementary_checks/no_persona/no_persona_effect.py", ".", [f"bundles.l2.{m}" for m in M])
# ---- 7 W1 roll-call vote prediction (Junsol Kim's proposal) and extensions ----
step("votes.v0", "python 01_select_rollcalls.py", V, ["map.s4", "fetch"])
step("votes.v3", "python 02_build_prompts.py", V, ["votes.v0"])
step("votes.v3b", "python 03_build_swap_prompts.py", V, ["votes.v3"])
step("checks.w1_prompts", "python 16_supplementary_checks/w1/vote_prompt_checks.py prompts", ".", ["votes.v3b"])
step("votes.v5_synthetic", "python estimate_votes.py --synthetic", V, ["votes.v0"])        # W1 gate 2: planted effect, recovery, reconstruction
SELS = ["pilot", "economic", "swap_abortion", "swap_economic"]
for m in M:
    for s in SELS:
        step(f"votes.v4.{m}.{s}", f"python 04_score_votes.py --model {m} --select {s}", V, ["votes.v3b"], gpu=True, shards=SH.get("v4", 1))
    step(f"votes.v5.{m}", f"python estimate_votes.py --model {m} --select v2", V, [f"votes.v4.{m}.{s}" for s in SELS] + ["votes.v5_synthetic"])
    step(f"votes.v5c.{m}", f"python 06_competence_by_party.py {m}", V, [f"votes.v5.{m}"])
V5 = [f"votes.v5.{m}" for m in M]
step("checks.order_corr", "python 16_supplementary_checks/w1/order_corr.py", ".", V5)
step("checks.cases", "python 16_supplementary_checks/cases/case_votes.py", ".", V5 + ["votes.v0"])   # named cases for the manuscript (2026-10-25)
step("votes.A12_loo_cp", "python 08_leave_one_out_cp.py", V, V5 + ["scales.issue_scales"])
step("votes.A13_error_direction", "python 09_error_direction.py", V, V5)
# guns: G0 scale, G1 benchmark, G2 votes (A14)
step("gunscale.g0_candidates", "python 01_find_candidates.py", G, ["scales.issue_scales"])
step("gunscale.g0_labels_claude", "python 02_claude_labels.py", G, ["gunscale.g0_candidates"])
step("gunscale.g0_scale", "python 03_build_gun_scale.py", G, ["gunscale.g0_candidates", "map.s3.qwen", "scales.issue_scales"])
step("gunscale.g1", "python 05_map_benchmark.py", G, ["gunscale.g0_scale"] + S3)
step("votes.g2_rollcalls", "python 10_gun_rollcalls.py", V, ["gunscale.g0_scale", "votes.v0"])
step("votes.g2_descriptions", "python 11_gun_descriptions.py", V, ["votes.g2_rollcalls"])
step("votes.g2_prompts", "python 12_gun_prompts.py", V, ["votes.g2_descriptions", "votes.v3b"])
for m in M:
    for s in ("guns", "swap_guns"):
        step(f"votes.v4.{m}.{s}", f"python 04_score_votes.py --model {m} --select {s}", V, ["votes.g2_prompts"], gpu=True, shards=SH.get("v4", 1))
step("votes.g2_gate", "python 13_gun_estimate.py --gate", V, ["votes.g2_prompts", "gunscale.g0_scale"])
for m in M:
    step(f"votes.g2_estimate.{m}", f"python 13_gun_estimate.py --model {m}", V, [f"votes.v4.{m}.guns", f"votes.v4.{m}.swap_guns", "votes.g2_gate", f"votes.v5.{m}"])
    step(f"votes.g2_diagnose.{m}", f"python 14_gun_diagnose.py {m}", V, [f"votes.g2_estimate.{m}"])
step("votes.g2_error_direction", "python 15_gun_error_direction.py", V, [f"votes.g2_estimate.{m}" for m in M] + ["votes.A13_error_direction"])
# ---- 8 entropy: W1 uncertainty, error warning and map-vote link (W, L1), Study N ----
step("uncertainty.prepare", "python code/01_prepare_input.py", "07_vote_uncertainty", V5 + [f"votes.g2_estimate.{m}" for m in M])   # + gun frames (PROTOCOL_GUNSYM)
step("uncertainty.run", f"{RSCRIPT} --vanilla 07_vote_uncertainty/code/02_fit_entropy.R", ".", ["uncertainty.prepare"])
step("warning.synthetic", "python error_warning.py --synthetic", "08_error_warning/code")
step("warning.run", "python error_warning.py", "08_error_warning/code", V5 + ["warning.synthetic", "map.s4"])
step("named.R1b", "python 01_check_rows.py", f"{N}/code", ["map.s4"])
for m in M:
    step(f"named.map.{m}", f"python 02_reproject_map.py --model {m}", f"{N}/code", [f"map.s3.{m}"], gpu=True)
    step(f"named.R1.{m}", f"python 03_compare_map.py --model {m}", f"{N}/code", [f"named.map.{m}", "map.s4"])
    step(f"named.R2.{m}", f"python 04_score_yes_no.py --model {m} --r2", f"{N}/code", [f"map.s5.{m}"], gpu=True)
    step(f"named.yesno.{m}", f"python 04_score_yes_no.py --model {m}", f"{N}/code", ["named.R1b", f"named.R1.{m}", f"named.R2.{m}"], gpu=True, shards=SH.get("n2_yesno", 1))
    step(f"named.prepare.{m}", f"python 05_prepare_rows.py --model {m}", f"{N}/analysis", [f"named.yesno.{m}", "gunscale.g0_scale"])
    step(f"named.prepare_fake.{m}", f"python 05_prepare_rows.py --model {m} --fake", f"{N}/analysis", [f"named.map.{m}", "named.R1b", "gunscale.g0_scale"])
step("named.run_fake", f"{RSCRIPT} --vanilla {N}/analysis/07_fit_main.R data_fake " + " ".join(M), ".", [f"named.prepare_fake.{m}" for m in M])
step("named.run", f"{RSCRIPT} --vanilla {N}/analysis/07_fit_main.R data " + " ".join(M), ".", [f"named.prepare.{m}" for m in M] + ["named.run_fake"])
# ---- 9 history: T0, T2, Nokken-Poole (N1), GMP (N2) ----
step("history.t0_synthetic", "python party_history.py --synthetic", T)
step("history.t0", "python party_history.py", T, S3 + ["history.t0_synthetic", "fetch"])
step("history.t2", "python 02_sorting.py", T, S3 + ["gunscale.g0_scale", "scales.issue_scales"])
step("nominate.n1_synthetic", "python nokken_poole.py --synthetic", "11_nominate_benchmarks/code")
step("nominate.n1", "python nokken_poole.py", "11_nominate_benchmarks/code", S3 + ["nominate.n1_synthetic", "history.t0"])
step("nominate.n2", "python 02_gmp_fit.py", "11_nominate_benchmarks/code", V5 + ["votes.g2_estimate.llama", "map.s4"])
# ---- 10 speech partisanship (S) and state lean (D) ----
SD = "12_speech_and_state/code"
step("speech.s0", "python 01_build_speech_matrices.py", SD, ["fetch"])
step("speech.s0_gate", "python 01_build_speech_matrices.py --gate", SD, ["speech.s0"])
step("speech.s1_synthetic", "python speech_history.py --synthetic", SD)
step("speech.s1", "python speech_history.py", SD, ["speech.s0_gate", "speech.s1_synthetic", "history.t0"] + S3)
step("speech.s2", "python 03_member_speech.py", SD, ["speech.s0_gate", "map.s4"] + V5)
step("speech.d_synthetic", "python state_lean.py --synthetic", SD)
step("speech.d", "python state_lean.py", SD, ["speech.d_synthetic", "map.s4", "votes.g2_estimate.llama"] + V5)
# ---- 11 gap fill ----
GF = "13_coverage_fill/code"
GF_DEPS = ["speech.s1", "speech.s2", "speech.d", "nominate.n1", "nominate.n2", "warning.run", "gunscale.g1"] + [f"votes.g2_estimate.{m}" for m in M]
step("fill.synthetic", "python 01_fill_gaps.py --synthetic", GF, GF_DEPS)    # the synthetic check plants effects on the real design (gun rows, maps)
step("fill.run", "python 01_fill_gaps.py", GF, ["fill.synthetic"] + GF_DEPS)
# ---- 11b guns as the symmetric social benchmark (PROTOCOL_GUNSYM, author 2026-10-24): same scripts, social scale = G0 gun scale ----
GUNENV = {"ISSUE_SCALES": str(R / "14_gun_symmetry" / "out" / "issue_scales_guns.csv"), "SOCIAL_TAG": "_guns"}
step("gunsym.scales", "python 01_make_gun_scales.py", "14_gun_symmetry/code", ["gunscale.g0_scale", "scales.issue_scales"])
step("map.s4_guns", "python 06_vote_vs_map.py --out s4_guns", D, S3 + ["gunsym.scales"], env=GUNENV)
step("map.s4d_guns", "python 09_within_party_by_era.py --out s4d_guns", D, S3 + ["gunsym.scales"], env=GUNENV)
step("checks.benchmark_guns", "python 16_supplementary_checks/benchmark/benchmark_recall.py", ".", ["map.s4_guns"], env=GUNENV)
step("checks.noise_benchmark_guns", "python 16_supplementary_checks/noise_benchmark/noise_benchmark.py", ".", ["checks.benchmark_guns"], env=GUNENV)
step("checks.members_by_era_guns", "python 16_supplementary_checks/members_by_era/members_by_era.py", ".", ["map.s4_guns", "map.s4c_positions"], env=GUNENV)
step("named.guns", f"{RSCRIPT} --vanilla {N}/analysis/09_fit_guns.R " + " ".join(M), ".", ["named.run"])
# ---- 12 Study M (mechanism) ----
SM = "15_mechanism/code"
for s, f in (("synth_check", "00a_synth_x1"), ("synth_check_x2", "00b_synth_x2"), ("synth_check_x3", "00c_synth_x3"),
             ("synth_check_x4", "00d_synth_x4"), ("synth_check_x5", "00e_synth_x5")):
    step(f"mechanism.{s}", f"python {f}.py", SM)
step("mechanism.X1", "python 01_x1_where_misses_go.py", SM, ["mechanism.synth_check", "map.s4", "map.s5_analyze"])
step("mechanism.X2", "python 02_x2_within_party.py", SM, ["mechanism.synth_check_x2", "map.s4d"])
step("mechanism.X1_guns", "python 01_x1_where_misses_go.py", SM, ["mechanism.synth_check", "map.s4_guns", "map.s5_analyze"], env=GUNENV)
step("mechanism.X2_guns", "python 02_x2_within_party.py", SM, ["mechanism.synth_check_x2", "map.s4d_guns"], env=GUNENV)
step("mechanism.X3", "python 04_x3_strength.py", SM, ["mechanism.synth_check_x3"] + [f"bundles.l2.{m}" for m in M])
for m in M:
    step(f"mechanism.X4_familiarity.{m}", f"python 05_x4_familiarity.py --model {m}", SM, [f"bundles.l2.{m}"], gpu=True)
    step(f"mechanism.X5_layers.{m}", f"python 08_x5_layers.py --model {m}", SM, [f"bundles.l1.{m}"], gpu=True)
    step(f"mechanism.X5_reproduce.{m}", f"python 09_x5_reproduce.py --model {m}", SM, [f"mechanism.X5_layers.{m}"])
step("mechanism.X4", "python analyze_x4.py", SM, ["mechanism.synth_check_x4"] + [f"mechanism.X4_familiarity.{m}" for m in M])
step("mechanism.X5A", "python 07_x5_stage_a.py", SM, ["mechanism.synth_check_x5"] + [f"bundles.l2.{m}" for m in M])
step("mechanism.X5B", "python 10_x5_stage_b.py", SM, [f"mechanism.X5_reproduce.{m}" for m in M])
step("mechanism.X5_threeway", "python 11_x5_threeway.py", SM, ["mechanism.X5A", "mechanism.X5B"])


def expand():
    """GPU steps with shards > 1 become <name>#i steps; the parent becomes a no-op that depends on its shards."""
    out = {}
    for s in STEPS.values():
        if s["shards"] > 1:
            kids = []
            for i in range(s["shards"]):
                k = dict(s, name=f"{s['name']}#{i}", cmd=f"{s['cmd']} --shard {i}/{s['shards']}", shards=1); out[k["name"]] = k; kids.append(k["name"])
            out[s["name"]] = dict(s, cmd=None, gpu=False, deps=kids, shards=1)
        else:
            out[s["name"]] = s
    return out


def needed(steps, target):
    keep, todo = set(), [target]
    while todo:
        n = todo.pop()
        if n in keep: continue
        keep.add(n); todo += steps[n]["deps"]
    return {k: v for k, v in steps.items() if k in keep}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--path", choices=["A", "B"]); ap.add_argument("--until"); ap.add_argument("--list", action="store_true")
    ap.add_argument("--keep-going", action="store_true", help="diagnostic runs only: after a failure keep running steps that do not depend on it")
    a = ap.parse_args()
    steps = expand()
    for s in steps.values():
        for d in s["deps"]: assert d in steps, (s["name"], d)
    if a.until: steps = needed(steps, a.until)
    if a.list:
        for s in steps.values(): print(("GPU " if s["gpu"] else "    ") + s["name"], "<-", ", ".join(s["deps"]))
        return
    assert a.path, "--path A or --path B"
    LOGS.mkdir(parents=True, exist_ok=True)
    rj = LOGS / f"run_path{a.path}.json"
    run = json.load(open(rj)) if rj.exists() else {"path": a.path, "config": CFG, "python": sys.version, "platform": platform.platform(), "steps": {}}
    if rj.exists() and run.get("config") != CFG:       # done markers carry no configuration (Codex round 3): never resume across a change
        sys.exit(f"{rj.name} was written under a different config/run.json: run python tools/clear_outputs.py --yes and start again")
    done = lambda n: (LOGS / f"done_{n}").exists()
    if a.path == "A" and ((LOGS / "PATH_B_MARKERS").exists() or (LOGS / "run_pathB.json").exists()):   # Path B marks GPU steps done
        sys.exit("Path B markers are present: run python tools/clear_outputs.py --yes before a full Path A run")   # (Codex review 2026-10-24)
    if a.path == "B":                      # GPU steps (and the CPU steps inside GPU chains) are not run; their shipped outputs are used
        (LOGS / "PATH_B_MARKERS").touch()  # written before any marker, so an interrupted Path B still blocks a later Path A
        for s in steps.values():
            if s["gpu"] or not s["path_b"]: (LOGS / f"done_{s['name']}").touch()
    gpu_slots, cpu_slots = int(CFG.get("gpu_processes", 2)), int(CFG.get("cpu_processes", 3))
    threads = str(max(1, (os.cpu_count() or 8) // max(1, cpu_slots)))
    running, failed, failed_all = {}, None, set()
    t_start = time.time()

    def blocked(n, seen=None):
        """True if n depends (transitively) on a failed step"""
        seen = seen or set()
        for d in steps[n]["deps"]:
            if d in failed_all or (d not in seen and (seen.add(d) or blocked(d, seen))): return True
        return False
    while True:
        for n, (p, s, t0, fh) in list(running.items()):
            rc = p.poll()
            if rc is None: continue
            fh.close(); del running[n]
            run["steps"][n] = dict(cmd=s["cmd"], cwd=s["cwd"], gpu=s["gpu"], start=time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(t0)),
                                   seconds=round(time.time() - t0, 1), exit=rc)
            json.dump(run, open(rj, "w"), indent=1)
            if rc == 0: (LOGS / f"done_{n}").touch(); print(time.strftime("%H:%M:%S"), "done", n, f"{time.time() - t0:.0f}s", flush=True)
            else: failed = failed or n; failed_all.add(n); print(time.strftime("%H:%M:%S"), "FAILED", n, "see", LOGS / f"{n}.log", flush=True)
        for n, s in steps.items():
            if done(n) or n in running or n in failed_all: continue
            if failed and (not a.keep_going or blocked(n)): continue
            if not all(done(d) for d in s["deps"]): continue
            if s["cmd"] is None: (LOGS / f"done_{n}").touch(); continue
            busy_gpu = sum(1 for _, (_, x, _, _) in running.items() if x["gpu"]); busy_cpu = len(running) - busy_gpu
            gb_used = sum(x["gb"] for _, (_, x, _, _) in running.items())
            if s["gpu"] and (busy_gpu >= gpu_slots or gb_used + s["gb"] > CFG["gpu_gb"]["total"]): continue
            if not s["gpu"] and busy_cpu >= cpu_slots: continue
            env = dict(os.environ, PYTHONIOENCODING="utf-8", HF_HUB_OFFLINE=os.environ.get("HF_HUB_OFFLINE", "1"),
                       OMP_NUM_THREADS=threads, MKL_NUM_THREADS=threads, OPENBLAS_NUM_THREADS=threads, GPU_GB=str(s["gb"] or 0),
                       CUBLAS_WORKSPACE_CONFIG=":4096:8", **s["env"])        # deterministic cuBLAS (common/loader.py deterministic())
            fh = open(LOGS / f"{n}.log", "a"); fh.write(f"$ (cd {s['cwd']}) {s['cmd']}\n"); fh.flush()
            p = subprocess.Popen(s["cmd"], shell=True, cwd=R / s["cwd"], env=env, stdout=fh, stderr=subprocess.STDOUT, executable="/bin/bash")
            running[n] = (p, s, time.time(), fh); print(time.strftime("%H:%M:%S"), "start", n, flush=True)
        if not running:
            break
        time.sleep(2)
    left = [n for n in steps if not done(n)]
    run["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S"); run["wall_seconds_this_call"] = round(time.time() - t_start)
    run["failed"] = failed; run["failed_all"] = sorted(failed_all); run["not_done"] = left
    json.dump(run, open(rj, "w"), indent=1)
    print("FAILED at", failed if failed else "", "| not done:", len(left)) if (failed or left) else print("all", len(steps), "steps done")
    sys.exit(1 if (failed or left) else 0)


if __name__ == "__main__":
    main()
