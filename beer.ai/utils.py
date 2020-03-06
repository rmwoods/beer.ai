import json
import pandas as pd


def get_style_guide():
    with open("styleguide.json") as f:
        style_guide = json.load(f)


def scale_ferm(df):
    """
    (DataFrame) -> float
    Compute the scaled fermentable quantity.

    Take as input a subset of the ing DataFrame, joined to the core DataFrame.
    Replace ferm_amount with the gravity contribution of the fermentable:
        g/L extract in the boil kettle.
    """
    df["ferm_amount"] = (
        df["ferm_amount"] * df["ferm_yield"] * df["efficiency"] / df["boil_size"]
    )
    df["ferm_amount"] = df["ferm_amount"].replace([np.inf, -np.inf], np.nan)
    return df


def scale_hop(df):
    """
    (DataFrame) -> float
    Compute the scaled hop quantity.

    Take as input a subset of the ing DataFrame, joined to the core DataFrame.
    Return a different quantity depending on the use:
        Dry hops:  dry hopping rate
            grams of dry hops per litre in the batch
        Boil hops: AUU
            grams of alpha acids per litre in the boil kettle
    """
    # Dry hops
    dh_cond = df["hop_use"] == "dry hop"
    df.loc[dh_cond, "hop_amount"] = (
        df.loc[dh_cond, "hop_amount"] / df.loc[dh_cond, "batch_size"]
    )

    # Every other hop use
    bh_cond = df["hop_use"] != "dry hop"
    df.loc[bh_cond, "hop_amount"] = (
        df.loc[bh_cond, "hop_amount"]
        * df.loc[bh_cond, "hop_alpha"]
        * (1 - 0.1 * (df.loc[bh_cond, "hop_form"] == "leaf").astype(int))
        / df.loc[bh_cond, "boil_size"]
    )
    df["hop_amount"] = df["hop_amount"].replace([np.inf, -np.inf], np.nan)
    return df


def scale_misc(df):
    """
    (DataFrame) -> float
    Compute the scaled misc quantity.

    Take as input a subset of the ing DataFrame, joined to the core DataFrame.
    Return a scaled misc quantity.
    """
    df["misc_amount"] = df["misc_amount"] / df["batch_size"]
    df["misc_amount"] = df["misc_amount"].replace([np.inf, -np.inf], np.nan)
    return df


def scale_yeast(df):
    """
    (DataFrame) -> DataFrame
    Return a DataFrame with a new column yeast_amount = 1
    """
    df.loc[~df["yeast_name"].isna(), "yeast_amount"] = 1
    return df


def ibu(df):
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
        Assumed columns are:
            "hop_scaled" - concentration of alpha acids in the kettle (g/L)
            "hop_time" - duration of boil following hop addition (minutes)
    Return:
    =======
    IBU: float
        Estimate of IBU for the given recipes.
    """
    pass


def gravity_kettle():
    """
    Return the kettle full gravity of a recipe
    """
    pass


def srm(df):
    """Return SRM (Standard Reference Method units), a measure of colour, for a
    recipe. 
    Use the Morey formula:
    (Source: https://web.archive.org/web/20100402141609/http://www.brewingtechniques.com/brewingtechniques/beerslaw/morey.html)

        SRM = 1.4922 * (sum of MCU over the grain bill) ^ 0.6859 
        MCU =  grain color * grain weight / kettle volume

        Where:
            grain color is in L
            grain weight is in lbs
            kettle volume is in gallons

    Parameters:
    ===========
    df: Pandas DataFrame
        DataFrame containing scaled fermentable quantities and fermentable
        colors. Assumed columns are "ferm_scaled" and "ferm_color"

    Return:
    =======
    srm: float
        Estimate of the SRM for the given recipes.
    """
    pass


def color(*args, **kwargs):
    # self.__doc__ = srm.__doc__??
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
