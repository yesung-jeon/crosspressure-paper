"""Median split used by every quadrant in the package.
Within each cell, values above the median are 'high'; members tied at the median go to whichever half makes the split closer to
50/50, and stay in the lower half when both are equally close. Scores are rounded upstream (TIE_DECIMALS), so ties are exact.
Why: in 114 House and 108/109 Senate more than half the members tie at the most pro-life abortion score; under the old rule nobody was
'high' and every member was classed progressive."""
import numpy as np
import pandas as pd


def _one(s):
    s = pd.Series(s, dtype=float); ok = s.notna(); v = s[ok]
    out = pd.Series(False, index=s.index)
    if len(v) == 0:
        return out
    m = v.median(); n = len(v); a = int((v > m).sum()); t = int((v == m).sum())
    up = abs(2 * (a + t) - n) < abs(2 * a - n)              # ties up only if strictly more balanced (integer counts: exact)
    out.loc[v.index] = ((v > m) | ((v == m) & up)).to_numpy()   # positional assignment keeps the bool dtype (review 10-30: a shorter
    return out.astype(bool)                                         # aligned Series upcast to object when a cell held NaN)


def split_hi(values, groups=None):
    """values: Series; groups: Series/list of Series (cell keys) or None for one cell. Returns a boolean Series ('high'); NaN -> False."""
    values = pd.Series(values)
    if groups is None:
        return _one(values)
    out = values.groupby(groups, group_keys=False).apply(_one).reindex(values.index)
    return pd.Series(np.where(out.isna(), False, out.to_numpy()).astype(bool), index=values.index)   # NaN cell key: False (as documented)


if __name__ == "__main__":      # unit check
    top = pd.Series([1.0] * 6 + [0.0, 0.2, 0.3, 0.4])               # 60% tied at the top: old rule -> 0 high; new -> 6 high
    assert split_hi(top).sum() == 6, split_hi(top).sum()
    bot = pd.Series([0.0] * 6 + [0.5, 0.6, 0.7, 0.8])               # 60% tied at the bottom: ties stay low -> 4 high (as old)
    assert split_hi(bot).sum() == 4
    mid = pd.Series([0.1, 0.2, 0.5, 0.5, 0.9, 1.0])                  # tie at median, balanced either way -> lower (old rule): 2 high
    assert split_hi(mid).sum() == 2
    rng = np.random.default_rng(0); x = pd.Series(rng.normal(size=1001)); g = pd.Series(rng.integers(0, 5, 1001))
    old = x > x.groupby(g).transform("median")
    assert (split_hi(x, g) == old).all()                             # no ties: identical to the old rule
    gx = pd.Series([1.0] * 6 + [0.0, 0.2, 0.3, 0.4] + [0.1, 0.2, 0.5, 0.5, 0.9, 1.0]); gg = pd.Series([0] * 10 + [1] * 6)
    assert split_hi(gx, gg).sum() == 8 and split_hi(gx, gg).index.equals(gx.index)
    na = split_hi(pd.Series([1.0, np.nan, 3.0, 4.0]))                # NaN values: False, dtype bool, ~ is logical
    assert na.dtype == bool and list(na) == [False, False, False, True] and list(~na) == [True, True, True, False]
    nk = split_hi(pd.Series([1.0, 2.0, 3.0, 4.0]), pd.Series(["a", "a", None, "b"]))   # NaN cell key: False, dtype bool
    assert nk.dtype == bool and list(nk) == [False, True, False, False]
    alln = split_hi(pd.Series([np.nan, np.nan, 1.0, 2.0]), pd.Series([0, 0, 1, 1]))
    assert alln.dtype == bool and list(alln) == [False, False, False, True]
    print("split_hi unit check passed")
