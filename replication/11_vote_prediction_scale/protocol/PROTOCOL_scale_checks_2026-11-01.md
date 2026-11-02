# Scale competence and scale error warning (2026-11-01)

Why: (a) the scale tasks had not been tested against the competence rule that the two-answer tasks use; (b) the claim that the models'
doubt does not flag their errors rested on an AUROC computed from two-answer YEA/NAY entropy only, while the paper's headline
uncertainty measure is the 1-9 scale. Written before any of the quantities below were computed.

Code: `11_vote_prediction_scale/code/scale_checks.py` (CPU; writes `../out/scale_checks.json`).

C1. Vote-task scale competence, A5 rule unchanged (`estimate_votes.competence`): share = s_yea (mean of the two scale directions),
    correct = correct_scale, on the scale sample (format failures dropped, both scale directions valid), per model and issue
    (abortion, economic, guns). Competent = aligned accuracy 95% roll-call bootstrap interval above 0.5 and party-gap correlation
    interval above 0. Same seed as the two-answer rule.
C2. Named-member scale competence, the named-member rule (`07_fit_main.R`): aligned (vote_cp = 0) mean of C_scale with a member-cluster
    bootstrap (2,000 draws, seed from dc.seed_for("N-scale-comp", model, task)), competent if the lower bound > 0.5 and the
    format-failure share < 0.10; for the 1-7 task and, when scored, the 1-9 task.
C3. Scale error warning. Same definitions as `17_error_warning` (metrics, auc_within, boot_diff with 1,000 member draws within party,
    seed dc.seed_for("EW-scale", model, issue)), with H = scale entropy (mean over the two directions of the 9-digit entropy / log2 9)
    and err = 1 - correct_scale. Rows: the abortion scale sample. Primary: AUROC within roll call for aligned and cross-pressured
    members and the cross-pressured minus aligned difference, per model. Secondary: scale entropy against two-answer errors.
    Code check (gate, stop on failure): the same functions with H = two-answer entropy and err = 1 - correct_avg reproduce the
    two-answer AUROC values to 1e-12.
Reading: estimates with 95% intervals; an AUROC difference is read only when its interval excludes 0. No Holm family (descriptive
check of a claim already in the paper). If C1 fails for a model and issue, its scale rows in the paper are labelled not interpreted.
