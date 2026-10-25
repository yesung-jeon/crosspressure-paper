#!/usr/bin/env python
"""Build the manuscript from templates. Steps: values.py -> tables.py -> fill every paper/sections/*.template.md into the same name
without ".template" ({{KEY}} from values.json; {{TABLE1}}-{{TABLE3}} insert paper/tables/*.md) -> assemble paper/manuscript.md (body:
sections 00-08) and paper/appendix.md (sections A-G) -> checks. A missing key stops the build. No number is typed in templates.

Checks: numeric gate (every number in the filled text must exist in values.json, the tables or the headline table; years and small
integers skipped, as in tools/numeric_gate.py); no em dashes; abstract 150-200 words (SSCR) once the abstract has prose.
Usage: python paper/build.py"""
import json, re, subprocess, sys
from pathlib import Path

P = Path(__file__).resolve().parent; R = P.parent
GATE = R / "tools" / "numeric_gate.py"   # number check shipped with the package
for s in ("values.py", "appendix_values.py", "tables.py", "appendix_items.py"):
    subprocess.run([sys.executable, str(P / s)], check=True)
V = json.load(open(P / "values.json", encoding="utf-8"))
AV = json.load(open(P / "appendix_values.json", encoding="utf-8"))   # appendix-only numbers read from package outputs
assert not set(V) & set(AV), sorted(set(V) & set(AV)); V.update(AV)
TAB = {f"TABLE{i}": (P / "tables" / f"table{i}.md").read_text(encoding="utf-8").strip() for i in (1, 2, 3)}
TAB.update({n.upper(): (P / "tables" / f"{n}.md").read_text(encoding="utf-8").strip() for n in ("items_profiles", "items_packages")})
# figures need matplotlib, kept out of the analysis environment (environment/requirements-paper.txt): drawn with a separate
# interpreter, $PAPER_PYTHON or ~/venvs/paperfig. Without it the build stops, so a manuscript is never built on stale figures.
import os
FIGPY = Path(os.environ.get("PAPER_PYTHON", Path.home() / "venvs/paperfig/bin/python"))
if not FIGPY.exists():
    sys.exit(f"figure interpreter not found: {FIGPY}. Create it with environment/requirements-paper.txt (see README) or set PAPER_PYTHON.")
for s in ("appendix_figures.py", "body_figures.py"): subprocess.run([str(FIGPY), str(P / s)], check=True)
# figure checksums: written each build; compared with the reference copy shipped with the package (differences are reported, not
# fatal, because another machine's libraries can change pixels without changing the plotted values)
import hashlib
FIGS = sorted((P / "figures").glob("*/*.p[dn][fg]"))
cur = {str(f.relative_to(P)): hashlib.sha256(f.read_bytes()).hexdigest() for f in FIGS}
ref_file = P / "figures" / "FIGURES_SHA256.ref.json"
if ref_file.exists():
    ref = json.loads(ref_file.read_text(encoding="utf-8"))
    diff = sorted(k for k in set(ref) | set(cur) if ref.get(k) != cur.get(k))
    print(f"figures: {len(cur)} files, " + ("identical to the reference" if not diff else f"{len(diff)} differ from the reference: {diff}"))
(P / "figures" / "FIGURES_SHA256.json").write_text(json.dumps(cur, indent=1) + "\n", encoding="utf-8")
KEY = re.compile(r"\{\{([A-Z0-9_]+)\}\}")
used, missing = set(), []


def fill(t):
    def sub(m):
        k = m.group(1)
        if k in TAB: return TAB[k]
        if k not in V: missing.append(k); return m.group(0)
        used.add(k); return V[k]["value"]
    # placeholders inside HTML comments (planning notes) are left as written
    return "".join(part if part.startswith("<!--") else KEY.sub(sub, part) for part in re.split(r"(<!--.*?-->)", t, flags=re.S))


tpls = sorted((P / "sections").glob("*.template.md"))
for t in tpls:
    (t.parent / t.name.replace(".template", "")).write_text(fill(t.read_text(encoding="utf-8")), encoding="utf-8")
if missing: sys.exit(f"missing keys: {sorted(set(missing))}")
strip = lambda s: re.sub(r"<!--.*?-->\s*", "", s, flags=re.S).strip()
filled = [t.parent / t.name.replace(".template", "") for t in tpls]
body = [p for p in filled if re.match(r"0\d_", p.name)]; app = [p for p in filled if re.match(r"[A-G]_", p.name)]


def merge_refs(texts):
    """One APA reference list for the body (author decision, 2026-10-25). Each section template keeps its own list, so a
    citation stays next to the section that uses it; here the lists are removed from the sections, duplicates must be identical
    text (otherwise the build stops), and the union is sorted by author names, then year. Legal sources (e.g. "129 Cong. Rec.")
    file under their reporter name."""
    bodies, refs = [], {}
    for t in texts:
        parts = re.split(r"^## References.*$", t, maxsplit=1, flags=re.M)
        bodies.append(parts[0].rstrip())
        for e in (x.strip() for x in (parts[1].split("\n\n") if len(parts) > 1 else []) if x.strip() and not x.strip().startswith("(")):  # "(No new citations ...)" notes
            k = re.sub(r"\s+", " ", e)
            m = re.match(r"^(\D.*?\(\d{4}[^)]*\))", k); head = m.group(1) if m else k   # authors and year identify a work
            prev = refs.get(head)
            if prev is not None and prev != k: sys.exit(f"reference entry differs between sections:\n{prev}\n{k}")
            refs[head] = k

    def key(e):
        s = re.sub(r"^\d+\s+", "", e)                                   # "129 Cong. Rec. ..." -> "Cong. Rec. ..."
        names = s.split("(")[0]
        year = (re.search(r"\((\d{4})", s) or re.search(r"(\d{4})", s) or [None, "0"])[1]
        return (re.sub(r"[^a-z ]", "", names.lower().replace("&", " ")).split(), year, s.lower())
    merged = sorted(refs.values(), key=key)
    body_txt = "\n\n".join(bodies)
    for e in merged:   # every listed work must be cited somewhere in the body
        first = re.sub(r"^\d+\s+", "", e).split(",")[0].split(".")[0].split(" (")[0].strip()
        if first.split()[-1] not in body_txt: sys.exit(f"reference not cited in the body: {e[:80]}")
    return body_txt + "\n\n# References\n\n" + "\n\n".join(merged)


(P / "manuscript.md").write_text(merge_refs([strip(p.read_text(encoding="utf-8")) for p in body]) + "\n", encoding="utf-8")
(P / "appendix.md").write_text("\n\n".join(strip(p.read_text(encoding="utf-8")) for p in app) + "\n", encoding="utf-8")
(P / "used_keys.json").write_text(json.dumps(sorted(used), indent=0) + "\n", encoding="utf-8")
print(f"filled {len(tpls)} templates; {len(used)} of {len(V)} keys used")

bad = 0
for doc in ("manuscript.md", "appendix.md"):
    txt = (P / doc).read_text(encoding="utf-8")
    if "—" in txt: print(f"{doc}: em dash found"); bad += 1
    # reference lists (DOIs, page ranges, volumes) are not results: gate the text with them removed
    gd = P / "_gate"; gd.mkdir(exist_ok=True)
    gtxt = re.sub(r"^#+ References.*?(?=^# |\Z)", "", txt, flags=re.S | re.M)
    for name in ("Qwen2.5-7B-Instruct", "Llama-3.1-8B-Instruct", "GPT-4.1-mini"): gtxt = gtxt.replace(name, "MODEL")   # model names carry version digits
    gtxt = re.sub(r"\d+\s+Cong\.\s+Rec\.\s+\d+", "CONGREC", gtxt)   # legal citations to the Congressional Record (volume, page)
    gtxt = re.sub(r"\((\d{4}), pp?\. \d+(?:–\d+)?\)", r"(\1, PAGE)", gtxt)   # pinpoint pages in author-year citations, e.g. (2014, p. 45)
    (gd / doc).write_text(gtxt, encoding="utf-8")
    g = subprocess.run([sys.executable, str(GATE), str(gd / doc), "--outputs", str(P / "values.json"), str(P / "appendix_values.json"), str(P / "tables"),
                        str(R / "validation" / "headline_values.csv")], capture_output=True, text=True)
    print(f"{doc}: " + (g.stdout.strip().splitlines() or ["(no gate output)"])[-1]); bad += g.returncode != 0
ab = P / "sections" / "00_abstract.md"
if ab.exists():
    words = len(strip(ab.read_text(encoding="utf-8")).split("# Abstract", 1)[-1].split())   # text after the heading (the title sits above it)
    if words > 20 and not 150 <= words <= 200: print(f"abstract: {words} words (SSCR 150-200)"); bad += 1
    print(f"abstract: {words} words")
sys.exit(1 if bad else 0)
