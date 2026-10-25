# Study N with the gun-defined CP (rebuild PROTOCOL_GUNSYM, author 2026-10-24: guns and abortion are symmetric social benchmarks).
# Run from replication/:  Rscript --vanilla 09_named_member_entropy/analysis/run_guns.R <model> [<model> ...]
# The Q2 grid of run.R (outcomes, FE, clusters, samples) with key = gun_cp on the Study N rows that have a gun label (G0 cells), and the
# same grid with key = vote_cp (abortion CP) on exactly those rows; secondary C_gun ~ gun_cp (as C_vote ~ vote_cp). Same verdict rules
# and minimum effect as run.R; competence from results/tables/competence.csv; the gun cells form their own Holm family.
# Writes 09_named_member_entropy/analysis/results_guns/.
suppressPackageStartupMessages({library(arrow); library(digest)})
MS <- commandArgs(trailingOnly = TRUE)
A <- "09_named_member_entropy/analysis"; OUTD <- file.path(A, "results_guns")
source(file.path(A, "helpers.R")); fits_init(OUTD)
for (m in MS) {
  d <- as.data.table(read_parquet(file.path(A, "data", paste0("rows_", m, ".parquet"))))[is.finite(gun_cp)]
  d[, gun_cp := as.integer(gun_cp)]
  SAMP <- list(all = d, dem = d[party == "Democrat"], rep = d[party == "Republican"], known = d[known == 1], no_i4 = d[i4 == 0])
  FES <- list(pcc = "fe", cc = "cc"); CLS <- list(member = "icpsr", twoway = c("icpsr", "congress"))
  for (q in c("Q2gun", "Q2ab_same_rows")) {
    key <- if (q == "Q2gun") "gun_cp" else "vote_cp"
    for (y in c("H", "H_yn", "H_econ", "H_soc", "H_avgp")) for (fn in names(FES)) for (cn in names(CLS)) for (sn in names(SAMP)) {
      rhs <- key; if (fn == "cc" && !sn %in% c("dem", "rep")) rhs <- c(key, "party_dem")
      fit(SAMP[[sn]], y, rhs, FES[[fn]], CLS[[cn]], paste(q, y, fn, cn, sn, m, sep = "__"), key_term = key, save_input = FALSE)
    }
  }
  fit(d, "C_gun", "gun_cp", "fe", "icpsr", paste("sec_Cgun", "C_gun", "pcc", "member", "all", m, sep = "__"), key_term = "gun_cp")
  fit(d, "C_vote", "vote_cp", "fe", "icpsr", paste("sec_Cvote_same_rows", "C_vote", "pcc", "member", "all", m, sep = "__"), key_term = "vote_cp")
}
chk <- fits_finish()
C <- fread(file.path(A, "results", "tables", "competence.csv"))
co <- fread(file.path(OUTD, "tables/coefficients.csv"))
co[, c("spec", "y", "fe", "cl", "sample", "model") := tstrsplit(tag, "__", fixed = TRUE)]
v <- co[y == "H" & fe == "pcc" & cl == "member" & sample == "all" & spec %in% c("Q2gun", "Q2ab_same_rows") & term %in% c("gun_cp", "vote_cp")]
v <- merge(v, C[, .(model, competent)], by = "model")
v[, verdict := fifelse((lower95 > 0 | upper95 < 0) & estimate >= 0.05, "more uncertain",
               fifelse((lower95 > 0 | upper95 < 0) & estimate <= -0.05, "less uncertain",
               fifelse(lower90 >= -0.05 & upper90 <= 0.05, "no meaningful difference", "undetermined")))]
v[competent == TRUE & spec == "Q2gun", p_holm := p.adjust(p, "holm")]
s2 <- co[spec %in% c("sec_Cgun", "sec_Cvote_same_rows") & term %in% c("gun_cp", "vote_cp")]
s2[, verdict := fifelse(upper95 < 0 & estimate <= -0.05, "less consistent with own votes",
                fifelse(lower90 >= -0.05 & upper90 <= 0.05, "no meaningful difference", "undetermined"))]
cv <- fread(file.path(OUTD, "tables/coverage.csv"))[, .(tag, observations)]
v <- merge(v, cv, by = "tag", sort = FALSE)
fwrite(v[, .(model, spec, term, competent, observations, estimate, se, lower95, upper95, lower90, upper90, p, p_holm, verdict)],
       file.path(OUTD, "tables/verdicts.csv"))
fwrite(s2[, .(model, spec, term, estimate, lower95, upper95, lower90, upper90, verdict)], file.path(OUTD, "tables/verdicts_secondary.csv"))
print(v[, .(model, spec, n = observations, est = round(estimate, 4), lo95 = round(lower95, 4), hi95 = round(upper95, 4), verdict)])
cat("fits:", nrow(chk), " max coefficient error", max(chk$coefficient_error), " max variance error", max(chk$variance_error), "\n")
