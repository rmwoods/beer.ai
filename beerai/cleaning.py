from utils import split_series_on_range
import pandas as pd
import numpy as np


def clean_efficiency(series, acceptable_min=0.5, acceptable_max=1.0):
    """
    Clean the "efficiency" column of the core DataFrame.

    Replace unacceptable values with the mean acceptable value for 
    all recipes. 

    Parameters
    ==========
    series: Series
        The "efficiency" column of the core DataFrame.
    acceptable_min: float
        The lowest efficiency to accept. Default: 0.5
    acceptable_max: float    
        The highest efficiency to accept. Default: 1.0

    Return: 
    =======
    Series representing the cleaned "efficiency" column. 
    """
    acceptable, unacceptable = split_series_on_range(
        series, acceptable_min, acceptable_max
    )
    mean_acceptable = acceptable.groupby(acceptable.index).first().mean()
    efficiency_cleaned = acceptable.append(
        pd.Series(index=unacceptable.index, data=mean_acceptable)
    ).sort_index()
    return efficiency_cleaned


def clean_ferm_yield(df, ferm_yield_cutoff=0.03, exceptions=None):
    """
    Clean the "ferm_yield" column of the core DataFrame.

    Replace unacceptable values with the mean acceptable value for 
    that fermentable's "ferm_type". Do not replace values for fermentables
    whose "ferm_name" is in the list of exceptions.

    Parameters
    ==========
    df: DataFrame
        The ingredients DataFrame.
    ferm_yield_cutoff: float
        The lowest value of ferm_yield to accept. Default: 0.03
    exceptions: list of str
        The values of ferm_name for which ferm_yield will be left intact.
        Default: ["rice hulls"] 

    Return: 
    =======
    Series representing the cleaned "ferm_yield" column.
    """
    if exceptions is None:
        exceptions = ["rice hulls"]

    acceptable_mask, unacceptable_mask = split_series_on_range(
        df["ferm_yield"], ferm_yield_cutoff, 1, return_mask=True
    )
    exceptions_mask = df["ferm_name"].isin(exceptions)

    # Identify average yield for each ferm_type amongst the good ones
    ferm_type_to_yield = (
        df.loc[acceptable_mask].groupby("ferm_type")["ferm_yield"].mean()
    )

    to_fix_mask = unacceptable_mask & ~exceptions_mask
    # Get rows to fix, set indices to iloc indices. For the bad ones, map their
    # ferm type to the average ferm_yield for that type.
    ferm_yield_cleaned = df.loc[to_fix_mask, "ferm_type"].map(ferm_type_to_yield)
    ferm_yield_cleaned.index = np.where(to_fix_mask)[0]
    # Get good ones, set indices to iloc indices
    ferm_yield_untouched = df.loc[~to_fix_mask, "ferm_yield"]
    ferm_yield_untouched.index = np.where(~to_fix_mask)[0]
    # Append and fix index back to original
    ferm_yield = ferm_yield_cleaned.append(ferm_yield_untouched).sort_index()
    ferm_yield.index = df.index

    return ferm_yield
