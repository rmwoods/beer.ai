from .utils import split_series_on_range


def clean_efficiency(series, acceptable_min=0.5, acceptable_max=1.0):
    """XXX"""
    acceptable, unacceptable = split_series_on_range(
        series, acceptable_min, acceptable_max
    )
    mean_acceptable = acceptable.groupby(acceptable.index).first().mean()
    efficiency_fixed = acceptable.append(pd.Series(index=unacceptable.index, data=mean_acceptable)).sort_index()
    return efficiency_fixed


def clean_yield(df, ferm_yield_cutoff=0.03, exceptions=None):
    """XXX"""
    if exceptions is None:
        exceptions = ["rice hulls"]

    unacceptable_mask, acceptable_mask = split_series_on_range(
        df["ferm_yield"], 0, ferm_yield_cutoff, return_mask=True
    )
    exceptions_mask = df["ferm_name"].isin(exceptions)

    # Identify average yield for each ferm_type amongst the good ones
    ferm_type_to_yield = (
        df.loc[acceptable_mask].groupby("ferm_type")["ferm_yield"].mean()
    )

    to_fix_mask = unacceptable_mask & ~exceptions_mask
    # Get rows to fix, set indices to iloc indices. For the bad ones, map their
    # ferm type to the average ferm_yield for that type.
    ferm_yield_fixed = df.loc[to_fix_mask, "ferm_type"].map(ferm_type_to_yield)
    ferm_yield_fixed.index = np.where(to_fix_mask)[0]
    # Get good ones, set indices to iloc indices
    ferm_yield_untouched = df.loc[~to_fix_mask, "ferm_yield"]
    ferm_yield_untouched.index = np.where(~to_fix_mask)[0]
    # Append and fix index back to original
    ferm_yield = ferm_yield_fixed.append(ferm_yield_untouched).sort_index()
    ferm_yield.index = df.index

    return ferm_yield
