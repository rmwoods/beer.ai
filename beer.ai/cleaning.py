
def adjust_efficiency(df, sugar_efficiency=1, lme_efficiency=1):
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

    # Sugar types: "sugar", "dry extract"
    sugar_types = ["sugar", "dry extract"]
    # lme types: "liquid extract", "extract"
    lme_types = ["liquid extract", "extract"]
    # all others -> keep recipe efficiency
    sugar_mask = df["ferm_type"].isin(sugar_types)
    sugar_inds = np.where(sugar_mask)[0]
    lme_mask = df["ferm_type"].isin(lme_types)
    lme_inds = np.where(lme_mask)[0]
    other_mask = ~sugar_mask & ~lme_mask
    other_inds = np.where(other_mask)[0]

    sugar_eff = pd.Series(sugar_efficiency * np.ones(len(sugar_inds)), index=sugar_inds)
    lme_eff = pd.Series(lme_efficiency * np.ones(len(lme_inds)), index=lme_inds)
    other_eff = df.loc[other_mask, "efficiency"]
    other_eff.index = other_inds

    total = sugar_eff.append(lme_eff)
    total = total.append(other_eff).sort_index()
    total.index = df.index
    return total


