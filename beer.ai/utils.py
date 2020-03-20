import json
import numpy as np


def get_style_guide():
    with open("styleguide.json") as f:
        return json.load(f)


def scale_ferm(df, new_col="ferm_amount"):
    """
    (DataFrame) -> float
    Compute the scaled fermentable quantity.

    XXX - update to describe parameters, expected columns in df.

    Take as input a subset of the ing DataFrame, joined to the core DataFrame.
    Replace ferm_amount with the gravity contribution of the fermentable:
        g/L extract in the boil kettle.
    """
    df[new_col] = (
        df["ferm_amount"] * df["ferm_yield"] * df["efficiency"] / df["boil_size"]
    )
    df[new_col] = df[new_col].replace([np.inf, -np.inf], np.nan)


def scale_hop(df, new_col="hop_amount"):
    """
    (DataFrame) -> float
    Compute the scaled hop quantity.

    XXX - update to describe parameters, expected columns in df.

    Take as input a subset of the ing DataFrame, joined to the core DataFrame.
    Return a different quantity depending on the use:
        Dry hops:  dry hopping rate
            kilograms of dry hops per litre in the batch
        Boil hops: AUU
            kilograms of alpha acids per litre in the boil kettle
    """
    # Dry hops
    dh_cond = df["hop_use"] == "dry hop"
    df.loc[dh_cond, new_col] = (
        df.loc[dh_cond, "hop_amount"] / df.loc[dh_cond, "batch_size"]
    )

    # Every other hop use
    bh_cond = df["hop_use"] != "dry hop"
    df.loc[bh_cond, new_col] = (
        df.loc[bh_cond, "hop_amount"]
        * df.loc[bh_cond, "hop_alpha"]
        * (1 - 0.1 * (df.loc[bh_cond, "hop_form"] == "leaf").astype(int))
        / df.loc[bh_cond, "boil_size"]
    )
    df[new_col] = df[new_col].replace([np.inf, -np.inf], np.nan)


def scale_misc(df, new_col="misc_amount"):
    """
    (DataFrame) -> float
    Compute the scaled misc quantity.

    XXX - update to describe parameters, expected columns in df.

    Take as input a subset of the ing DataFrame, joined to the core DataFrame.
    Return a scaled misc quantity.
    """
    df[new_col] = df["misc_amount"] / df["batch_size"]
    df[new_col] = df[new_col].replace([np.inf, -np.inf], np.nan)


def scale_yeast(df, new_col="yeast_amount"):
    """
    (DataFrame) -> DataFrame
    Return a DataFrame with a new column yeast_amount = 1
    """
    df.loc[~df["yeast_name"].isna(), new_col] = 1


def ibu(df, hop_col="hop_amount"):
    """Return IBU (International Bitterness Units), a measure of bitterness, for a
    recipe.
    Use the Tinseth formula:
    (Source: https://realbeer.com/hops/research.html, Glenn Tinseth)

        IBUs = utilization * mg/L alpha acids
        utilization = bigness factor * boil time factor
        bigness factor = 1.65 * 0.000125^(wort gravity - 1)
        boil time factor = (1 - e^(-0.04 * time)) / 4.15

        Where:
            wort gravity is in SG (eg. 1.051)
            time is in minutes

    Parameters:
    ===========
    df: Panadas DataFrame
        Dataframe containing scaled hop quantities and addition times.
        Dataframe assumed to have "hop_time" as a column, which represents the
        duration of boil following hop addition in minutes.
    hop_col: str, default "hop_amount"
        Name of column containing **scaled** hop quantities.

    Return:
    =======
    Dataframe with "ibu" column added to passed in Dataframe
        Estimate of IBU for the given recipes.
    """
    # if hops_col not in df.columns:
    #    scale_hop(df, hop_col)
    # Get rid of dry hops
    sub_df = df.loc[:, df["hop_use"] != "dry hop"]
    # Turn kg/L to mg/L
    hop_amount = sub_df[hop_col] * 1000 * 1000

    boil_time_factor = (1 - np.exp(-0.04 * sub_df["hop_time"])) / 4.15
    bigness_factor = 1.65 * 0.000125 ** (gravity_kettle_sg(sub_df["ferm_amount"]) - 1)
    utilization = boil_time_factor * bigness_factor
    ibu = (utilization * hop_amount).sum()
    ibu.name = "ibu"
    return df.merge(ibu, left_index=True, right_index=True, how="left")


def gravity_kettle_sg(s):
    """Take a series containing scaled fermentables and calculate the kettle
    full gravity of the recipe, in SG (eg. 1.050).


    XXX - Add formula in doc, source for it

    Parameters
    ==========
    s: Series
        Series of fermentable amounts

    Return
    ======
    Series
        Series representing full grabity for recipes.
    """
    # XXX - I think this is supposed to sum per recipe, but we're currently
    # just summing all the recipes into a single number.

    return 1 + 0.10 * 4 * s.groupby(s.index).sum()


def srm(df, ferm_col="ferm_amount", srm_name="srm"):
    """Return SRM (Standard Reference Method units), a measure of colour, for a
    recipe.
    Use the Morey formula:
    (Source: https://web.archive.org/web/20100402141609/http://www.brewingtechniques.com/brewingtechniques/beerslaw/morey.html)

        SRM = 1.4922 * (sum of MCU over the grain bill) ^ 0.6859
        MCU =  grain color * grain weight / kettle volume

        Where:
            grain color is in °L (degrees Lovabond)
            grain weight is in lbs
            kettle volume is in gallons

    Parameters:
    ===========
    df: Pandas DataFrame
        DataFrame containing scaled fermentable quantities and fermentable
        colors. Assumed column is "ferm_color".
    ferm_col: str, default "ferm_amount"
        Name of column containing **scaled** fermentables
    srm_name: str, default "srm"
        Name of column that will contain SRM estimate.

    Return:
    =======
    Dataframe with new column `color_name` which is an estimate of the SRM for
    the given recipes.
    """
    # ferm_amount in kg, boil_size in kg
    kg_to_lb = 0.453592
    l_to_gal = 0.264172
    mcu = df["ferm_color"] * df[ferm_col] * kg_to_lb / (df["boil_size"] * l_to_gal)
    srm = 1.4922 * mcu.groupby(mcu.index).sum() ** 0.6859
    srm.name = "srm"
    return df.merge(srm, left_index=True, right_index=True, how="left")


def color(*args, **kwargs):
    """This is a convenience function, see `srm` for documentation.

    NOTE: This function passes `srm_name = "color"` to `srm` unless it has
    already been specified.
    """
    if "srm_name" not in kwargs.keys():
        kwargs.update({"srm_name": "color"})
    return srm(*args, **kwargs)


def abv(df):
    """Return ABV (Alcohol By Volume) for a recipe.
    Use the following formulae:
    (Source: "Brewing Calculations" by Jim Helmke, D.G. Yuengling & Son
    MBAA Brewing and Malting Science Course, Fall 2016, Madison)

        ABV = 1.25 * ABW
        ABW = 0.42 * (OE - attenuation * OE)
        OE is determined by solving the quadratic:
            extract = OE * (1 + 0.004 * OE)

        Where:
            OE is in degrees Plato
            attenuation is a %
            extract is in kg/hL = 0.01 * (kg/L)

    Parameters:
    ===========
    df: Pandas DataFrame
        DataFrame containing scaled fermentable quantities and yeast
        attenuations. Assumed column names are "ferm_scaled" and
        "yeast_attenuation".

    Return:
    =======
    abv: float
        Estimate of the ABV for the given recipes.
    """
    pass
