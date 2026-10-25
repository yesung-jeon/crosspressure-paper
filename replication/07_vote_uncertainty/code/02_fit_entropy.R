# W1 uncertainty (PROTOCOL.md, sealed in PROTOCOL_SEAL.json). Run from replication/
#   Rscript --vanilla 07_vote_uncertainty/run.R (from replication/; rebuild of kim/review/w1_uncertainty_2026-10-22)
# Order: 0 protocol hash, 1 frozen baseline (W1 §6.1 accuracy, one cell per model x issue), 2 synthetic check, 3 grid, 4 verdicts and descriptives.
suppressPackageStartupMessages({library(arrow); library(digest)})
D0 <- "07_vote_uncertainty"
source(file.path(D0, "code", "helpers.R")); fits_init(D0)
seal <- fromJSON(file.path(D0, "protocol", "PROTOCOL_SEAL.json"))
stopifnot(digest(file = file.path(D0, "protocol", "PROTOCOL.md"), algo = "sha256") == seal[["PROTOCOL.md"]])

d <- as.data.table(read_parquet(file.path(D0, "data/w1_uncertainty_input.parquet")))
M <- c("qwen", "llama"); IS <- c("abortion", "economic"); INTERP <- c("llama", "qwen")
# Rebuild PROTOCOL_GUNSYM (author 2026-10-24): gun-vote cells run through the same grid and verdict rule; the baseline (section 1)
# stays on the W1 cells, gun cells form their own Holm family, and a model is interpreted on gun votes only if G2 found it competent.
IS_GUN <- intersect(c("guns", "guns_gcp"), unique(d$issue)); IS_ALL <- c(IS, IS_GUN)
GUN_COMPETENT <- M[vapply(M, function(m) isTRUE(fromJSON(sprintf("06_vote_prediction/out/g2/estimates_%s.json", m))$competence$competent), TRUE)]
sub <- function(m, i) d[model == m & issue == i]

# ---- 1. frozen baseline: the sealed W1 §6.1 accuracy coefficient and SE, all 6 cells -------------------------------------------
base <- list()
for (m in M) {
  est <- fromJSON(sprintf("06_vote_prediction/out/v5/estimates_v2_%s_abortion_economic.json", m))$by_issue
  for (i in IS) {
    reg <- est[[i]]$regressions; r <- reg[[grep("^accuracy", names(reg))[1]]]
    ct <- fit(sub(m, i), "correct_avg", "cp", "fe", c("icpsr", "key"), paste0("baseline__", m, "_", i), save_input = FALSE)
    db <- abs(ct$estimate - r$b); ds <- abs(ct$se - r$se)
    base[[paste(m, i)]] <- list(model = m, issue = i, sealed_b = r$b, refit_b = ct$estimate, sealed_se = r$se, refit_se = ct$se,
                                abs_diff_b = db, abs_diff_se = ds)
    if (db > 1e-6 || ds > 1e-6) stop(sprintf("baseline not reproduced: %s %s b %.3g se %.3g", m, i, db, ds))
  }
}
write_json(list(status = "reproduced", tolerance = 1e-6, cells = unname(base)), file.path(D0, "baseline_check.json"), auto_unbox = TRUE,
           pretty = TRUE, digits = 12)
cat(sprintf("baseline: %d of %d W1 accuracy coefficients and SEs reproduced\n", length(base), length(base)))

# ---- 2. synthetic check on the real design (Llama abortion rows) --------------------------------------------------------------
set.seed(20261022)
s <- copy(sub("llama", "abortion"))
re_k <- s[, .(k = unique(key))][, rk := rnorm(.N, 0, 0.05)]; re_m <- s[, .(icpsr = unique(icpsr))][, rm := rnorm(.N, 0, 0.05)]
s <- merge(merge(s, re_k, by.x = "key", by.y = "k"), re_m, by = "icpsr")
syn <- list()
for (eff in c(0.08, 0)) {
  s[, ysyn := 0.3 + eff * cp + rk + rm + rnorm(.N, 0, 0.2)]
  ct <- fit(s, "ysyn", "cp", "fe", c("icpsr", "key"), paste0("synthetic__planted_", eff), save_input = FALSE)
  ok <- if (eff > 0) ct$lower95 <= eff && eff <= ct$upper95 else ct$lower90 >= -0.05 && ct$upper90 <= 0.05
  syn[[as.character(eff)]] <- list(planted = eff, estimate = ct$estimate, ci95 = c(ct$lower95, ct$upper95), ci90 = c(ct$lower90, ct$upper90), pass = ok)
  if (!ok) stop("synthetic check failed for planted ", eff)
}
write_json(list(status = "passed", checks = unname(syn)), file.path(D0, "synthetic_check.json"), auto_unbox = TRUE, pretty = TRUE, digits = 10)
cat("synthetic: planted +0.08 recovered; planted 0 gives a 90% interval inside +-0.05\n")
.fits$res <- list(); .fits$covg <- list(); .fits$checks <- list()   # the grid tables hold only the protocol's cells

# ---- 3. specification grid (PROTOCOL table; every cell) -----------------------------------------------------------------------
for (m in M) for (i in IS_ALL) {
  q <- sub(m, i); tg <- function(x) paste0(x, "__", m, "_", i)
  fit(q, "H", "cp", "fe", c("icpsr", "key"), tg("main"))
  fit(q, "H_yf", "cp", "fe", c("icpsr", "key"), tg("yf"))
  fit(q, "H_nf", "cp", "fe", c("icpsr", "key"), tg("nf"))
  fit(q, "H_avg", "cp", "fe", c("icpsr", "key"), tg("havg"))
  fit(q, "H", c("cp", "party_dem"), "key", c("icpsr", "key"), tg("rc_only"))
  fit(q, "H", "cp", "fe", "icpsr", tg("cl_member"))
  fit(q, "H", "cp", "fe", "key", tg("cl_rollcall"))
  fit(q[party == "Democrat"], "H", "cp", "key", c("icpsr", "key"), tg("dem"))
  fit(q[party == "Republican"], "H", "cp", "key", c("icpsr", "key"), tg("rep"))
  fit(q[known == 1], "H", "cp", "fe", c("icpsr", "key"), tg("known"))
  fit(q[wrong == 1], "H", "cp", "fe", c("icpsr", "key"), tg("wrong"))
  fit(q[wrong == 0], "H", "cp", "fe", c("icpsr", "key"), tg("right"))
}
chk <- fits_finish()

# ---- 4. verdicts (main cell, PROTOCOL rule) and descriptives ------------------------------------------------------------------
co <- fread(file.path(D0, "tables/coefficients.csv"))[term == "cp"]
co[, c("spec", "cell") := tstrsplit(tag, "__", fixed = TRUE)][, `:=`(model = base::sub("_.*$", "", cell), issue = base::sub("^[^_]+_", "", cell))]   # issue may contain "_" (guns_gcp)
v <- co[spec == "main"]
v[, verdict := fifelse((lower95 > 0 | upper95 < 0) & estimate >= 0.05, "more uncertain for CP",
               fifelse((lower95 > 0 | upper95 < 0) & estimate <= -0.05, "less uncertain for CP",
               fifelse(lower90 >= -0.05 & upper90 <= 0.05, "no meaningful difference", "undetermined")))]
v[, interpreted := fifelse(issue %in% IS, model %in% INTERP, model %in% GUN_COMPETENT)]
v[interpreted == TRUE & issue %in% IS, p_holm := p.adjust(p, "holm")]          # the W1 family, unchanged by the gun cells
v[interpreted == TRUE & issue %in% IS_GUN, p_holm := p.adjust(p, "holm")]      # gun cells: their own family (PROTOCOL_GUNSYM)
fwrite(v[, .(model, issue, interpreted, estimate, se, lower95, upper95, lower90, upper90, p, p_holm, verdict)], file.path(D0, "tables/verdicts.csv"))
ds <- d[, .(n = .N, mean_H = mean(H), mean_H_yf = mean(H_yf), mean_H_nf = mean(H_nf), mean_H_avg = mean(H_avg),
            share_H_over_0.5 = mean(H > 0.5), accuracy = mean(correct_avg), mean_H_wrong = mean(H[wrong == 1]),
            mean_H_right = mean(H[wrong == 0])), by = .(model, issue, cp)][order(model, issue, cp)]
fwrite(ds, file.path(D0, "tables/descriptives.csv"))
print(v[, .(model, issue, interpreted, est = round(estimate, 4), lo95 = round(lower95, 4), hi95 = round(upper95, 4),
            lo90 = round(lower90, 4), hi90 = round(upper90, 4), p_holm = signif(p_holm, 3), verdict)])
cat("grid fits:", nrow(chk), " max coefficient error", max(chk$coefficient_error), " max variance error", max(chk$variance_error), "\n")
