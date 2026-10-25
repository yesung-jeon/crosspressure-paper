#!/usr/bin/env python3
"""Numeric gate: every number in the prose must exist in generated analysis output.
Shipped with the package (2026-10-25) so that paper/build.py can check every printed number; the helper strip_markup is included
in this file.

Modeled on Inbok Rhee's numeric gate ("prose numbers checked: 147, not found in generated
output: 0"). Catches numbers typed by hand, stale numbers after re-estimation, and numbers an
AI invented while polishing prose.

Usage:
  python numeric_gate.py PROSE_FILE --outputs DIR_OR_FILE [DIR_OR_FILE ...] [--keep-years] [--min 11]

Outputs are scanned recursively (.csv .tsv .md .txt .json .log .tex .html). By default, years
(1900-2100) and integers below --min (default 11) are skipped since they are usually counts in words.
"""
import re
import sys
from pathlib import Path


def strip_markup(text, suffix):
    text = re.sub(r"^---\n.*?\n---\n", "", text, flags=re.S)            # YAML header
    text = re.sub(r"```.*?```", "", text, flags=re.S)                    # code chunks
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    if suffix == ".tex":
        text = re.sub(r"(?<!\\)%.*", "", text)
        text = re.sub(r"\\begin\{(table|figure|equation|align)\*?\}.*?\\end\{\1\*?\}", "", text, flags=re.S)
        text = re.sub(r"\\(?:cite[pt]?|ref|label|eqref|autoref)\{[^}]*\}", "", text)
        text = re.sub(r"\\[a-zA-Z]+\*?(?:\[[^\]]*\])?\{([^}]*)\}", r"\1", text)
        text = re.sub(r"\\[a-zA-Z]+", "", text)
    text = re.sub(r"\[@[^\]]+\]|@[A-Za-z][\w:-]+", "", text)              # pandoc citations
    text = re.sub(r"^\s*\|.*\|\s*$", "", text, flags=re.M)               # markdown tables
    return text

NUM = re.compile(r"(?<![\w.])[-−]?\d{1,3}(?:,\d{3})+(?:\.\d+)?|(?<![\w.])[-−]?\d*\.?\d+")
EXT = {".csv", ".tsv", ".md", ".txt", ".json", ".log", ".tex", ".html"}


def canon(tok):
    t = tok.replace("−", "-").replace(",", "").lstrip("-")
    if t.startswith("."):
        t = "0" + t
    try:
        float(t)
    except ValueError:
        return None
    if "." in t:
        t = t.rstrip("0").rstrip(".") if not t.endswith(".") else t[:-1]
    return t


def corpus(paths):
    vals = set()
    for p in paths:
        p = Path(p)
        files = [p] if p.is_file() else [f for f in p.rglob("*") if f.suffix.lower() in EXT]
        for f in files:
            try:
                txt = f.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            for m in NUM.finditer(txt):
                c = canon(m.group(0))
                if c is None:
                    continue
                vals.add(c)
                if "." in c:  # allow prose rounding of a more precise output value
                    ip, dp = c.split(".")
                    for k in range(1, len(dp)):
                        vals.add(canon(f"{float(c):.{k}f}"))
    return vals


def main():
    if len(sys.argv) < 4 or "--outputs" not in sys.argv:
        print(__doc__)
        sys.exit(1)
    prose = Path(sys.argv[1])
    i = sys.argv.index("--outputs") + 1
    outs = []
    while i < len(sys.argv) and not sys.argv[i].startswith("--"):
        outs.append(sys.argv[i])
        i += 1
    keep_years = "--keep-years" in sys.argv
    min_int = int(sys.argv[sys.argv.index("--min") + 1]) if "--min" in sys.argv else 11

    vals = corpus(outs)
    text = strip_markup(prose.read_text(encoding="utf-8", errors="replace"), prose.suffix.lower())
    text = re.sub(r"\{[#@][^}]*\}|@(?:fig|tbl|sec|eq)-[\w-]+", "", text)  # cross-refs

    checked, missing = 0, []
    for m in NUM.finditer(text):
        c = canon(m.group(0))
        if c is None:
            continue
        if "." not in c:
            n = int(c)
            if n < min_int or (not keep_years and 1900 <= n <= 2100):
                continue
        checked += 1
        if c not in vals:
            line = text.count("\n", 0, m.start()) + 1
            ctx = re.sub(r"\s+", " ", text[max(0, m.start()-50):m.end()+30])
            missing.append((line, m.group(0), ctx))

    print(f"generated corpus: {len(vals)} distinct values from {len(outs)} path(s)")
    print(f"prose numbers checked: {checked}")
    print(f"not found in generated output: {len(missing)}")
    for line, tok, ctx in missing:
        print(f"  L{line}: {tok}   ...{ctx}...")
    sys.exit(1 if missing else 0)


if __name__ == "__main__":
    main()
