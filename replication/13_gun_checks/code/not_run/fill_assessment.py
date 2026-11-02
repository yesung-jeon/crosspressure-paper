#!/usr/bin/env python
"""Render ASSESSMENT.md from ASSESSMENT.template.md: every {{path|fmt}} token is filled from out/gf.json (or another JSON named by a
prefix), so no number in the assessment is typed.
  path: "/"-separated keys into the JSON (keys may contain dots, e.g. "1.0"); prefixes  sd_s1: speech_district s1.json,
        syn: out/synthetic.json
  fmt:  ci  -> "b [lo, hi]" (3 decimals; b and ci95 of a coefficient dict)   ci4 -> same with 4 decimals
        sh -> share [share_ci]   pc -> point [ci]   dd -> d [d_ci]   mw / nw / df -> N1 model_within / np_within / diff with intervals
        f3 / f4 -> number, 3 or 4 decimals   int -> integer with thousands separator   ciw -> "[lo, hi]" only
  python fill_assessment.py   -> ASSESSMENT.md (STOP on any unresolved token)
"""
import json, re
from pathlib import Path

R = Path(__file__).resolve().parents[1]
SRC = {"": json.loads((R / "out" / "gf.json").read_text()), "syn": json.loads((R / "out" / "synthetic.json").read_text()),
       "sd_s1": json.loads((R.parent / "12_speech_and_state" / "out" / "s1" / "s1.json").read_text())}   # rebuild path


def num(x, k):
    s = f"{x:.{k}f}"
    return s[1:] if s.startswith("-") and float(s) == 0 else s          # no "-0.000"


def get(path):
    pre, _, rest = path.partition(":") if ":" in path else ("", "", path)
    v = SRC[pre]
    for key in rest.split("/"): v = v[int(key)] if isinstance(v, list) else v[key]
    return v


PAIRS = {"ci": ("b", "ci95"), "sh": ("share", "share_ci"), "pc": ("point", "ci"), "dd": ("d", "d_ci"), "mw": ("model_within", "model_within_ci"),
         "nw": ("np_within", "np_within_ci"), "df": ("diff", "diff_ci")}


def render(tok):
    path, fmt = tok.split("|")
    v = get(path)
    if fmt in PAIRS or fmt == "ci4":
        k = 4 if fmt == "ci4" else 3; pk, ck = PAIRS.get(fmt, PAIRS["ci"]); ci = v[ck]
        return f"{num(v[pk], k)} [{num(ci[0], k)}, {num(ci[1], k)}]"
    if fmt == "ciw": return f"[{num(v[0], 3)}, {num(v[1], 3)}]"
    if fmt in ("f3", "f4"): return num(float(v), int(fmt[1]))
    if fmt == "int": return f"{int(v):,}"
    raise SystemExit(f"STOP: unknown format {fmt}")


text = (R / "ASSESSMENT.template.md").read_text(encoding="utf-8")
out = re.sub(r"\{\{([^}]+)\}\}", lambda m: render(m.group(1)), text)
assert "{{" not in out
(R / "ASSESSMENT.md").write_text(out, encoding="utf-8"); print("ASSESSMENT.md rendered,", len(re.findall(r"\{\{", text)), "tokens")
