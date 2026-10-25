#!/usr/bin/env python
"""G0 step 2b (PROTOCOL_G0 section 2): independent labels by GPT-4.1-mini (author approval 2026-10-22). Same ledger and pinned model as
Study V v2_verify.py; temperature 0, JSON output, cached and logged. The key comes from crosspressure/.env (OPENAI_API_KEY) through the
ledger; it is never printed or passed on the command line. The model sees only the Voteview roll-call text.

  python g0_labels_gpt.py --limit 5   # smoke
  python g0_labels_gpt.py             # all 234 contested candidates
"""
import argparse, json, sys
from pathlib import Path
import pandas as pd

G = Path(__file__).resolve().parents[1]; REPO = G.parents[1]
sys.path.insert(0, str(Path.home() / ".claude" / "kim-kit" / "scripts"))
from llm_ledger import Ledger  # noqa: E402

MODEL = "gpt-4.1-mini-2025-04-14"
O = G / "out" / "g0"
SYSTEM = ("You classify U.S. congressional roll-call votes for a research dataset. Answer only from the text given. Reply with JSON only.")
TEMPLATE = """ROLL-CALL TEXT (Voteview record)
{t}

Questions:
1. gun_control: Is this vote mainly about the regulation of firearms or ammunition (purchase, possession, carrying, manufacture, sale,
registration, background checks, waiting periods, liability of gun makers, funding for gun-control enforcement)? Answer "no" if guns are
incidental (for example military ammunition procurement, or a crime bill where the motion concerns another provision).
2. yea_direction: If gun_control is "yes", does a YEA vote move policy toward MORE firearm regulation ("stricter"), toward LESS regulation
("looser"), or can this not be told from the text ("unclear")? Take account of the motion: a YEA on a motion to table an amendment
rejects that amendment. If gun_control is "no", answer "".

Return JSON: {{"gun_control": "yes" or "no", "yea_direction": "stricter", "looser", "unclear" or "", "reason": "one short sentence"}}"""
PROMPT_FILE = G / "code" / "g0_gpt_prompt.txt"


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--limit", type=int); a = ap.parse_args()
    PROMPT_FILE.write_text(SYSTEM + "\n\n" + TEMPLATE, encoding="utf-8")
    c = pd.read_csv(O / "contested_texts.csv").fillna("")
    if a.limit: c = c.head(a.limit)
    L = Ledger(O / "gpt_ledger", dotenv=str(REPO / ".env"))
    out = []
    for i, r in c.iterrows():
        msg = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": TEMPLATE.format(t=r.t)}]
        txt = L.chat("openai", MODEL, msg, temperature=0, max_tokens=200, response_format={"type": "json_object"})
        try:
            j = json.loads(txt); ok = j.get("gun_control") in ("yes", "no") and j.get("yea_direction") in ("stricter", "looser", "unclear", "")
        except json.JSONDecodeError:
            j, ok = {}, False
        out.append(dict(key=r.key, parse_ok=ok, gun_control=j.get("gun_control"), yea_direction=j.get("yea_direction", ""),
                        reason=j.get("reason", "")))
        if (i + 1) % 50 == 0: print(i + 1, "labelled", flush=True)
    v = pd.DataFrame(out)
    v.to_csv(O / ("labels_gpt_smoke.csv" if a.limit else "labels_gpt.csv"), index=False, encoding="utf-8")
    print(dict(n=len(v), parse_failures=int((~v.parse_ok).sum()), gun=v.gun_control.value_counts().to_dict(),
               direction=v.yea_direction.value_counts().to_dict()))


if __name__ == "__main__":
    main()
