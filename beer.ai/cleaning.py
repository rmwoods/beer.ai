# OG Corrections from the Utils_Troubleshooting notebook:
# Correction 2: Replace efficiency below 0.5 with the mean (above 0.5) 
# ====================================================================
def split_series_on_range(series, min_value, max_value):
    inside_mask = series.between(min_value, max_value)
    inside = series[inside_mask]
    outside = series[~inside_mask]
    return inside, outside

def replace_with_mean(series, acceptable_min=0.5, acceptable_max=1.0):
    """ Replace unacceptable quantities in a series with the mean acceptable quantity. """
    good, bad = split_series_on_range(series, acceptable_min, acceptable_max)
    mean_good = good.groupby(good.index).first().mean()
    fixed_series = good.append(pd.Series(index=bad.index, data=mean_good))

# Correction 3: Replace efficiency for sugars and extracts with 1
# Shower thought:
#   Would it be better to make this correct instead by
#   introducing a new rule in gravity_wort:
#       use df["efficiency"] for grains and adjuncts
#       use 1 otherwise?
# ====================================================================

extract_types = ["sugar", "dry extract", "liquid extract", "extract"]
def adjust_efficiency(df, col_efficiency, ferm_types_extract, new_efficiency=1):
    """
    Return a Series of adjusted efficiencies based on the ferm_type / name.

    Efficiency can vary depending on what fermentable it is, what form it's
    in, and when it's added during the brew. Here, we assume the following:

        ferm_type:                                      efficiency
        ==========================================================
        malt, adjunct (added in mash):        efficiency as-stated
        dry malt extract, sugar (added to kettle): efficiency is 1
        liquid malt extract (added to kettle):     efficiency is 1 

    Parameters
    ==========
    ...

    Return
    ======
    Series representing efficiency of a particular fermentable
    """
    # Version from Jupyter Notebook
    extract_mask = df["ferm_type"].isin(ferm_types_extract)
    extract_inds = np.where(extract_mask)[0]
    other_mask = ~extract_mask
    other_inds = np.where(other_mask)[0]

    extract_eff = pd.Series(new_efficiency * np.ones(len(extract_inds)), index=extract_inds)
    other_eff = df.loc[other_mask, "efficiency"]
    other_eff.index = other_inds

    all_ferms = extract_eff.append(other_eff).sort_index()
    all_ferms.index = df.index
    return all_ferms

    # Previous version from utils.py
    ## Sugar types: "sugar", "dry extract"
    #sugar_types = ["sugar", "dry extract"]
    ## lme types: "liquid extract", "extract"
    #lme_types = ["liquid extract", "extract"]
    ## all others -> keep recipe efficiency
    #sugar_mask = df["ferm_type"].isin(sugar_types)
    #sugar_inds = np.where(sugar_mask)[0]
    #lme_mask = df["ferm_type"].isin(lme_types)
    #lme_inds = np.where(lme_mask)[0]
    #other_mask = ~sugar_mask & ~lme_mask
    #other_inds = np.where(other_mask)[0]

    #sugar_eff = pd.Series(sugar_efficiency * np.ones(len(sugar_inds)), index=sugar_inds)
    #lme_eff = pd.Series(lme_efficiency * np.ones(len(lme_inds)), index=lme_inds)
    #other_eff = df.loc[other_mask, "efficiency"]
    #other_eff.index = other_inds

    #total = sugar_eff.append(lme_eff)
    #total = total.append(other_eff).sort_index()
    #total.index = df.index
    #return total


# Correction 4: Replace ferm_yield below 0.03 with the mean above 0.03
#   For that ferm_type
#   Excluding ferm_name == 'rice hulls'
#
#   Should we do this using the same function we use for Correction 2?
# ====================================================================
ferm_yield_cutoff = 0.03
good_ferm_yield_mask = bf["ferm_yield"] > ferm_yield_cutoff
bad_ferm_yield_mask = bf["ferm_yield"] <= ferm_yield_cutoff
non_rice_hulls_mask = bf["ferm_name"] != "rice hulls"
ferm_yield_mean = bf[good_ferm_yield_mask & non_rice_hulls_mask].groupby("ferm_type")["ferm_yield"].mean()
ferm_yield_ind_to_replace = bf[bad_ferm_yield_mask & non_rice_hulls_mask].index

bf["ferm_yield_adj"] = bf["ferm_yield"]

bf.loc[ferm_yield_ind_to_replace, "ferm_yield_adj"] = bf.loc[ferm_yield_ind_to_replace, "ferm_type"].map(ferm_yield_mean)

# IBU corrections from the Utils_Troubleshooting notebook
utilization_factor=3.75
