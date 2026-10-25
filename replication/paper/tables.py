#!/usr/bin/env python
"""Write the main-text tables (paper/tables/table{1,2,3}.md) from paper/values.json. Cells hold {{KEY}} references resolved here, so
every number traces to a headline row. Run paper/values.py first.
Usage: python paper/tables.py"""
import json, re
from pathlib import Path

P = Path(__file__).resolve().parent
V = json.load(open(P / "values.json", encoding="utf-8"))
NA = "n/a"


def r(s):
    return re.sub(r"\{\{([A-Z0-9_]+)\}\}", lambda m: V[m.group(1)]["value"], s)


def both(fmt):
    return r(f"Qwen {fmt.format(s='Q')}; Llama {fmt.format(s='L')}")


def table(path, title, head, rows, notes):
    out = [f"**{title}**", "", "| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    out += ["| " + " | ".join(r(c) for c in row) + " |" for row in rows]
    out += [""] + [r(n) for n in notes]
    (P / "tables").mkdir(exist_ok=True)
    (P / "tables" / path).write_text("\n".join(out) + "\n", encoding="utf-8")


table("table1.md", "Table 1. The models' directions track members' roll-call positions",
      ["", "Qwen", "Llama"],
      [["Selected layer", "{{LAYER_Q}}", "{{LAYER_L}}"],
       ["r(economic coordinate, DW-NOMINATE dimension 1)", "{{R_X_DW1_Q}}", "{{R_X_DW1_L}}"],
       ["r(economic coordinate, economic roll-call scale)", "{{R_X_ECON_Q}}", "{{R_X_ECON_L}}"],
       ["r(social coordinate, abortion roll-call scale)", "{{R_Y_AB_Q}}", "{{R_Y_AB_L}}"],
       ["r(social coordinate, gun-control roll-call scale)", "{{R_Y_GUN_Q}}", "{{R_Y_GUN_L}}"],
       ["Party gap, economic direction", "{{PARTY_GAP_X_Q}}", "{{PARTY_GAP_X_L}}"],
       ["Party gap, social direction", "{{PARTY_GAP_Y_Q}}", "{{PARTY_GAP_Y_L}}"],
       ["Share of aligned member-Congresses in their own quadrant (abortion)", "{{RECALL_ALIGNED_AB_Q}}", "{{RECALL_ALIGNED_AB_L}}"],
       ["Share of aligned member-Congresses in their own quadrant (guns)", "{{RECALL_ALIGNED_GUN_Q}}", "{{RECALL_ALIGNED_GUN_L}}"]],
      ["Note. The correlation with DW-NOMINATE dimension 1 is the mean of correlations computed within each Congress; the other correlations are computed within Congress and chamber. Correlations and party gaps use the member-Congresses whose party the model names correctly; the shares in own quadrant use all Democratic and Republican member-Congresses with both scales (Appendix A.5). The same layer is chosen when the directions are extracted twice (Appendix A.4)."])

table("table2.md", "Table 2. Roll-call vote prediction: cross-pressured minus aligned members, within party and roll call",
      ["", "Qwen", "Llama"],
      [["Abortion: accuracy aligned / cross-pressured", "{{ACC_ALIGNED_AB_Q}} / {{ACC_CROSS_AB_Q}}", "{{ACC_ALIGNED_AB_L}} / {{ACC_CROSS_AB_L}}"],
       ["Abortion: coefficient", "{{CP_COEF_AB_Q}} {{CP_COEF_AB_Q_CI}}", "{{CP_COEF_AB_L}} {{CP_COEF_AB_L_CI}}"],
       ["Abortion: leave-one-out label", "{{CP_LOO_AB_Q}} {{CP_LOO_AB_Q_CI}}", "{{CP_LOO_AB_L}} {{CP_LOO_AB_L_CI}}"],
       ["Abortion: Democrats / Republicans", "{{CP_COEF_AB_DEMOCRAT_Q}} / {{CP_COEF_AB_REPUBLICAN_Q}}", "{{CP_COEF_AB_DEMOCRAT_L}} / {{CP_COEF_AB_REPUBLICAN_L}}"],
       ["Abortion: state-based cross-pressure","{{D3_AB_Q}} {{D3_AB_Q_CI}}", "{{D3_AB_L}} {{D3_AB_L_CI}}"],
       ["Economic: accuracy aligned / cross-pressured", "{{ACC_ALIGNED_ECON_Q}} / {{ACC_CROSS_ECON_Q}}", "{{ACC_ALIGNED_ECON_L}} / {{ACC_CROSS_ECON_L}}"],
       ["Economic: coefficient", "{{CP_COEF_ECON_Q}} {{CP_COEF_ECON_Q_CI}}", "{{CP_COEF_ECON_L}} {{CP_COEF_ECON_L_CI}}"],
       ["Guns: accuracy aligned / cross-pressured", "see Appendix D.5", "{{ACC_ALIGNED_GUN_L}} / {{ACC_CROSS_GUN_L}}"],
       ["Guns: coefficient, gun-defined (leave-one-out)", "see Appendix D.5", "{{CP_COEF_GUN_GUNCP_L}} {{CP_COEF_GUN_GUNCP_L_CI}}"],
       ["Guns: coefficient, abortion-defined", "see Appendix D.5", "{{CP_COEF_GUN_ABCP_L}} {{CP_COEF_GUN_ABCP_L_CI}}"]],
      ["Note. Coefficients: party x roll-call fixed effects, clustered by member and roll call; 95% intervals in brackets. Prompts and "
       "roll-call selection in Appendix D.1; Qwen's gun-vote results in Appendix D.5 and accuracy benchmarks in Appendix D.6."])

table("table3.md", "Table 3. Cross-pressured members are placed and predicted less faithfully across measures and definitions",
      ["Measure", "Abortion votes", "Gun votes", "Leave-one-out label", "State-based", "Stated positions"],
      [["Map: share in own quadrant, cross-pressured vs aligned",
        both("{{{{RECALL_CROSS_AB_{s}}}}} vs {{{{RECALL_ALIGNED_AB_{s}}}}}"), both("{{{{RECALL_CROSS_GUN_{s}}}}} vs {{{{RECALL_ALIGNED_GUN_{s}}}}}"), NA, NA, NA],
       ["Stated profiles: consistency, cross minus aligned", NA, NA, NA, NA, both("{{{{H3_{s}}}}}")],
       ["Behavior: vote accuracy coefficient",
        both("{{{{CP_COEF_AB_{s}}}}}"), "Llama {{CP_COEF_GUN_GUNCP_L}} (Qwen: Appendix D.5)", both("{{{{CP_LOO_AB_{s}}}}}"), both("{{{{D3_AB_{s}}}}}"), NA],
       ["Uncertainty: choice entropy, cross minus aligned (bits)",
        both("{{{{W1U_AB_{s}}}}}"), "Llama {{W1U_GUNCP_L}} (Qwen: Appendix D.5)", NA, NA, both("{{{{H1_{s}}}}}")]],
      ["Note. Reference: two-dimensional DW-NOMINATE places cross-pressured member-Congresses in their own quadrant at {{DW2_RECALL_CROSS_AB}} "
       "(aligned {{DW2_RECALL_ALIGNED_AB}}) on abortion. Economic votes show no deficit (Qwen {{CP_COEF_ECON_Q}}, Llama {{CP_COEF_ECON_L}}). "
       "Entropy differences are small: well under a tenth of a bit for votes. Llama places members' economic and "
       "social coordinates closer together than their votes are; Qwen shows the reverse (Appendix C.7). State-based: the member's state "
       "leans toward the other party in presidential elections (Appendix D.7)."])
print("paper/tables/table1.md, table2.md, table3.md written")
