# Study N analysis (PROTOCOL §4-6). Run from replication/:
#   Rscript --vanilla 09_named_member_entropy/analysis/run.R <data dir name: data|data_fake> <model> [<model> ...]
# Writes into 09_named_member_entropy/analysis/<out>/ where out = "results" for data, "results_fake" for data_fake.
# Order: protocol hash, competence, synthetic check, grid, verdicts and descriptives. helpers.R = review/w1_uncertainty_2026-10-22/helpers.R.
suppressPackageStartupMessages({library(arrow); library(digest)})
args <- commandArgs(trailingOnly = TRUE); src <- args[1]; MS <- args[-1]
A <- "09_named_member_entropy/analysis"; OUTD <- file.path(A, if (src == "data") "results" else "results_fake")
source(file.path(A, "helpers.R")); fits_init(OUTD)
seal <- fromJSON("09_named_member_entropy/protocol/PROTOCOL_SEAL.json")$sha256
stopifnot(digest(file = "09_named_member_entropy/protocol/PROTOCOL.md", algo = "sha256") == seal[["PROTOCOL.md"]])
set.seed(20261022)
boot_mean <- function(v, g, R = 2000) {          # member-cluster bootstrap of a mean
  s <- split(v, g); G <- length(s); m <- vapply(s, sum, 0); n <- vapply(s, length, 0)
  bs <- replicate(R, { k <- sample.int(G, G, replace = TRUE); sum(m[k]) / sum(n[k]) })
  c(est = sum(m) / sum(n), lo = unname(quantile(bs, .025)), hi = unname(quantile(bs, .975)))
}
comp <- list(); desc <- list()
for (m in MS) {
  d <- as.data.table(read_parquet(file.path(A, src, paste0("rows_", m, ".parquet"))))
  # ---- competence (aligned vote-quadrant rows; before any comparison by cross-pressure) ----
  al <- d[vote_cp == 0]; b <- boot_mean(al$C_vote, al$icpsr)
  fail <- mean(d$fail_share)
  comp[[m]] <- data.table(model = m, aligned_C_vote = b[["est"]], lo = b[["lo"]], hi = b[["hi"]], format_fail = fail,
                          competent = b[["lo"]] > 0.5 & fail < 0.10)
  # ---- synthetic check on this model's real design (first model only) ----
  if (m == MS[1]) {
    s <- copy(d); re <- s[, .(icpsr = unique(icpsr))][, rm := rnorm(.N, 0, 0.05)]; s <- merge(s, re, by = "icpsr")
    for (eff in c(0.08, 0)) {
      s[, ysyn := 0.3 + eff * vote_cp + rm + rnorm(.N, 0, 0.1)]
      ct <- fit(s, "ysyn", "vote_cp", "fe", "icpsr", paste0("synthetic__", eff), save_input = FALSE)
      ok <- if (eff > 0) ct$lower95 <= eff && eff <= ct$upper95 else ct$lower90 >= -0.05 && ct$upper90 <= 0.05
      if (!ok) stop("synthetic check failed for planted ", eff)
    }
    write_json(list(status = "passed", model = m), file.path(OUTD, "synthetic_check.json"), auto_unbox = TRUE)
    .fits$res <- list(); .fits$covg <- list(); .fits$checks <- list()
  }
  # ---- grid ----
  SAMP <- list(all = d, dem = d[party == "Democrat"], rep = d[party == "Republican"], known = d[known == 1], no_i4 = d[i4 == 0])
  FES <- list(pcc = "fe", cc = "cc"); CLS <- list(member = "icpsr", twoway = c("icpsr", "congress"))
  for (q in c("Q2", "Q3")) {
    key <- if (q == "Q2") "vote_cp" else "map_crossed"
    for (y in c("H", "H_yn", "H_econ", "H_soc", "H_avgp")) for (fn in names(FES)) for (cn in names(CLS)) for (sn in names(SAMP)) {
      rhs <- key; if (fn == "cc" && !sn %in% c("dem", "rep")) rhs <- c(key, "party_dem")
      main <- y == "H" && fn == "pcc" && cn == "member" && sn == "all"
      fit(SAMP[[sn]], y, rhs, FES[[fn]], CLS[[cn]], paste(q, y, fn, cn, sn, m, sep = "__"), key_term = key, save_input = main)
    }
  }
  one <- function(tag, y, rhs, key = rhs[1]) fit(d, y, rhs, "fe", "icpsr", paste(tag, y, "pcc", "member", "all", m, sep = "__"), key_term = key)
  one("joint", "H", c("vote_cp", "map_crossed"))
  one("cont_conflict", "H", c("conflict", "depth"))
  one("cont_abs", "H", c("abs_zx", "abs_zy", "zxzy"))
  one("Q5_vote", "H", c("vote_ELST", "vote_ERSP"))
  one("Q5_map", "H", c("map_ELST", "map_ERSP"))
  one("sec_Cvote", "C_vote", "vote_cp")
  one("sealedmap_Q3", "H", "map_crossed_sealed")
  one("sealedmap_conflict", "H", c("conflict_sealed", "depth_sealed"))
  # ---- descriptives ----
  t22 <- d[, .(n = .N, mean_H = mean(H), mean_C_vote = mean(C_vote)), by = .(vote_cp, map_crossed)][order(vote_cp, map_crossed)][, model := m]
  mis <- d[vote_cp == 1 & map_q != vote_q]; q4 <- boot_mean(mis$C_map - mis$C_vote, mis$icpsr)
  desc[[m]] <- list(table_2x2 = t22, Q4 = data.table(model = m, n = nrow(mis), mean_Cmap_minus_Cvote = q4[["est"]], lo = q4[["lo"]], hi = q4[["hi"]]),
                    by_vote_q = d[, .(n = .N, mean_H = mean(H)), by = vote_q][, model := m], by_map_q = d[, .(n = .N, mean_H = mean(H)), by = map_q][, model := m])
  rm(d, SAMP); invisible(gc(verbose = FALSE))
}
chk <- fits_finish()
C <- rbindlist(comp); fwrite(C, file.path(OUTD, "tables/competence.csv"))
for (k in c("table_2x2", "Q4", "by_vote_q", "by_map_q")) fwrite(rbindlist(lapply(desc, `[[`, k)), file.path(OUTD, paste0("tables/desc_", k, ".csv")))
co <- fread(file.path(OUTD, "tables/coefficients.csv"))
co[, c("spec", "y", "fe", "cl", "sample", "model") := tstrsplit(tag, "__", fixed = TRUE)]
v <- co[y == "H" & fe == "pcc" & cl == "member" & sample == "all" & spec %in% c("Q2", "Q3") & term %in% c("vote_cp", "map_crossed")]
v <- merge(v, C[, .(model, competent)], by = "model")
v[, verdict := fifelse((lower95 > 0 | upper95 < 0) & estimate >= 0.05, "more uncertain",
               fifelse((lower95 > 0 | upper95 < 0) & estimate <= -0.05, "less uncertain",
               fifelse(lower90 >= -0.05 & upper90 <= 0.05, "no meaningful difference", "undetermined")))]
v[competent == TRUE, p_holm := p.adjust(p, "holm")]
s2 <- co[spec == "sec_Cvote" & term == "vote_cp"]
s2[, verdict := fifelse(upper95 < 0 & estimate <= -0.05, "less consistent with own votes",
                fifelse(lower90 >= -0.05 & upper90 <= 0.05, "no meaningful difference", "undetermined"))]
fwrite(v[, .(model, spec, term, competent, estimate, se, lower95, upper95, lower90, upper90, p, p_holm, verdict)], file.path(OUTD, "tables/verdicts.csv"))
fwrite(s2[, .(model, estimate, lower95, upper95, lower90, upper90, verdict)], file.path(OUTD, "tables/verdicts_secondary.csv"))
cat("fits:", nrow(chk), " max coefficient error", max(chk$coefficient_error), " max variance error", max(chk$variance_error), "\n")
