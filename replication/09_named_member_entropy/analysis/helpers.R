# Verified fixed-effects fitting for W1 uncertainty, from ~/.claude/research-kit/templates/analysis/fit_helpers.R (Rhee,
# floor/review/broad_models_2026-09-28/helpers.R), extended to two-way clustering with the W1 §6.1 small-sample rule
# (kim/06_vote_prediction/code/estimate_votes.py twoway + kim-kit cluster_fit.py cr1_cov): each piece CR1 = G/(G-1) * (N-1)/(N-K), K = regressors +
# fixed-effect cells; V = V_c1 + V_c2 - V_c1xc2 (if not positive, the larger one-way piece). One-way clustering uses one piece.
# Every fit: fixest::feols estimate -> independent reconstruction of coefficients and variance from the demeaned design (stop above
# tol) -> model .rds, exact input rows .csv.gz, spec .json -> coverage and checks tables. No singleton pruning (W1 keeps all rows;
# a cell without variation in cp does not identify the coefficient and is reported as the identifying share).
suppressPackageStartupMessages({library(data.table); library(fixest); library(jsonlite)})
setDTthreads(1); setFixest_nthreads(1); setFixest_notes(FALSE)

.fits <- new.env()
fits_init <- function(dir) {
  .fits$dir <- dir; .fits$res <- list(); .fits$covg <- list(); .fits$checks <- list()
  for (d in c("models", "tables", "logs", "figures")) dir.create(file.path(dir, d), showWarnings = FALSE, recursive = TRUE)
  invisible(dir)
}
.write_tables <- function() {
  d <- .fits$dir
  fwrite(rbindlist(.fits$res, fill = TRUE), file.path(d, "tables/coefficients.csv"))
  fwrite(rbindlist(.fits$covg, fill = TRUE), file.path(d, "tables/coverage.csv"))
  fwrite(rbindlist(.fits$checks, fill = TRUE), file.path(d, "tables/regression_checks.csv"))
}

# CR1 piece for a cluster id vector g (scores = X * u, bread = (X'X)^-1)
.piece <- function(X, u, g, bread, N, K) {
  s <- rowsum(X * u, g, reorder = FALSE); G <- nrow(s)
  list(V = bread %*% crossprod(s) %*% bread * (G / (G - 1)) * ((N - 1) / (N - K)), G = G)
}

fit <- function(q, y, rhs, fe, cluster, tag, key_term = rhs[1], tol = 1e-7, save_input = TRUE) {
  stopifnot(!is.null(.fits$dir), is.data.table(q), length(fe) == 1, length(cluster) %in% 1:2)
  for (v in c(y, rhs, fe, cluster)) if (!v %in% names(q)) stop("missing column: ", v)
  if (any(!is.finite(q[[y]]))) stop("non-finite outcome in ", tag)
  f <- as.formula(paste(y, "~", paste(rhs, collapse = "+"), "|", fe), env = .GlobalEnv)
  a <- feols(f, q, vcov = as.formula(paste0("~", paste(cluster, collapse = "+"))),
             ssc = ssc(adj = TRUE, fixef.K = "full", cluster.adj = TRUE, cluster.df = "conventional", t.df = "min"),
             fixef.rm = "none", fixef.tol = 1e-10, fixef.iter = 100000, demeaned = TRUE)
  stopifnot(nobs(a) == nrow(q))
  used <- names(coef(a)); X <- a$X_demeaned[, used, drop = FALSE]; Y <- a$y_demeaned
  N <- nrow(q); nfe <- uniqueN(q[[fe]]); K <- length(used) + nfe
  bread <- solve(crossprod(X)); bb <- drop(bread %*% crossprod(X, Y)); u <- drop(Y - X %*% bb)
  g1 <- as.character(q[[cluster[1]]]); p1 <- .piece(X, u, g1, bread, N, K)
  if (length(cluster) == 2) {
    g2 <- as.character(q[[cluster[2]]]); p2 <- .piece(X, u, g2, bread, N, K); p12 <- .piece(X, u, paste(g1, g2, sep = "#"), bread, N, K)
    V <- p1$V + p2$V - p12$V
    if (any(diag(V) <= 0)) V <- if (p1$V[1, 1] >= p2$V[1, 1]) p1$V else p2$V
    Gs <- c(p1$G, p2$G)
  } else { V <- p1$V; Gs <- p1$G }
  ce <- max(abs(bb - coef(a))); ve <- max(abs(V - vcov(a)))
  if (ce >= tol || ve >= tol) stop(sprintf("Numerical reconstruction failed for %s: coef %.3g variance %.3g", tag, ce, ve))
  dfr <- min(Gs) - 1; se <- sqrt(diag(V))
  ct <- data.table(tag, outcome = y, term = used, estimate = bb, se = se,
                   lower95 = bb - qt(.975, dfr) * se, upper95 = bb + qt(.975, dfr) * se,
                   lower90 = bb - qt(.95, dfr) * se, upper90 = bb + qt(.95, dfr) * se,
                   p = 2 * pt(-abs(bb / se), dfr), df = dfr)
  cp_cells <- q[, .(v = uniqueN(get(key_term)) > 1, n = .N), by = fe]
  .fits$res[[tag]] <- ct
  .fits$covg[[tag]] <- data.table(tag, observations = N, fe_cells = nfe, clusters = paste(Gs, collapse = ";"),
                                  cluster_variables = paste(cluster, collapse = ";"), omitted = paste(a$collin.var, collapse = ";"),
                                  key_term, share_rows_in_identifying_cells = cp_cells[v == TRUE, sum(n)] / N)
  .fits$checks[[tag]] <- data.table(tag, coefficient_error = ce, variance_error = ve)
  if (save_input) {
    saveRDS(a, file.path(.fits$dir, "models", paste0(tag, ".rds")))
    fwrite(q[, unique(c(y, rhs, fe, cluster)), with = FALSE], file.path(.fits$dir, "models", paste0(tag, "_input.csv.gz")))
    write_json(list(tag = tag, outcome = y, rhs = used, fe = fe, cluster = cluster, n = N, fe_cells = nfe, clusters = Gs,
                    small_sample = "per piece G/(G-1)*(N-1)/(N-K), K = regressors + FE cells; two-way V = V1 + V2 - V12",
                    coefficients = as.list(bb), covariance = unname(V)),
               file.path(.fits$dir, "models", paste0(tag, "_spec.json")), auto_unbox = TRUE, pretty = TRUE, digits = 16)
  }
  .write_tables()
  cat(tag, "N", N, "G", paste(Gs, collapse = "/"), "\n"); flush.console()
  rm(a, X, Y, u); invisible(gc(verbose = FALSE))   # 2026-10-22: the first grid run ended silently after 48 fits; free memory per fit
  invisible(ct)
}

fits_finish <- function() {
  chk <- rbindlist(.fits$checks)
  write_json(list(status = "passed", models = nrow(chk), max_coefficient_error = max(chk$coefficient_error),
                  max_variance_error = max(chk$variance_error)),
             file.path(.fits$dir, "regression_verification.json"), auto_unbox = TRUE, pretty = TRUE)
  capture.output(sessionInfo(), file = file.path(.fits$dir, "logs/session_info.txt"))
  invisible(chk)
}
