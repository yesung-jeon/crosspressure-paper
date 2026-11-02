**Table D1. Vote prediction with two answers and on the nine-point scale: cross-pressured minus aligned members, within party and roll call**

|  | Qwen, YEA or NAY | Qwen, scale | Llama, YEA or NAY | Llama, scale |
|---|---|---|---|---|
| Abortion: accuracy aligned / cross-pressured | 0.554 / 0.486 | 0.528 / 0.435 | 0.693 / 0.531 | 0.634 / 0.554 |
| Abortion: coefficient | −0.048 [−0.079, −0.017] | −0.079 [−0.109, −0.050] | −0.112 [−0.159, −0.065] | −0.036 [−0.068, −0.005] |
| Abortion: coefficient, YEA described first only | 0.003 [−0.023, 0.029] | as above | −0.109 [−0.156, −0.062] | as above |
| Abortion: scale minus YEA-first coefficient | n/a | −0.082 [−0.120, −0.044] | n/a | 0.073 [0.020, 0.126] |
| Abortion: leave-one-out label | −0.049 [−0.081, −0.017] | −0.082 [−0.112, −0.053] | −0.105 [−0.151, −0.059] | −0.033 [−0.065, −0.002] |
| Abortion: Democrats / Republicans | −0.008 / −0.099 | −0.180 / 0.051 | −0.008 / −0.247 | 0.008 / −0.094 |
| Abortion: state-based cross-pressure | −0.035 [−0.056, −0.015] | −0.026 [−0.048, −0.003] | −0.054 [−0.075, −0.033] | −0.028 [−0.046, −0.010] |
| Economic: accuracy aligned / cross-pressured | 0.553 / 0.594 | 0.557 / 0.613 | 0.567 / 0.583 | 0.539 / 0.547 |
| Economic: coefficient | 0.021 [0.002, 0.039] | 0.032 [0.014, 0.051] | 0.013 [−0.008, 0.033] | 0.006 [−0.012, 0.024] |
| Guns: accuracy aligned / cross-pressured | see Appendix D.5 | see Appendix D.5 | 0.620 / 0.494 | 0.633 / 0.522 |
| Guns: coefficient, gun-defined (leave-one-out) | see Appendix D.5 | see Appendix D.5 | −0.189 [−0.245, −0.133] | −0.079 [−0.146, −0.012] |
| Guns: coefficient, abortion-defined | see Appendix D.5 | see Appendix D.5 | −0.093 [−0.131, −0.055] | −0.075 [−0.120, −0.031] |

Note. The YEA or NAY columns are the estimates of Section 6, averaged over the two answer orders (Figure 4 shows the coefficients), except the row with YEA described first only, which uses the scale's prompt; coefficients use party x roll-call fixed effects, clustered by member and roll call, with 95% intervals in brackets. Scale: the prediction is YEA when the average YEA lean of the two directions exceeds one half; same votes and estimator. On the scale Llama predicts YEA far more often than with two answers, so its scale accuracies partly reflect that lean (Appendix D.10).
