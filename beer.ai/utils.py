import json
import pandas as pd
import numpy as np
import math

def get_style_guide():
    with open("styleguide.json") as f:
        style_guide = json.load(f)


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
    # Get rid of dry hops
    df = df[df["hop_use"] != "dry hop"]
    # scale_hop returns g/L alpha acids in the kettle
    df_scaled = scale_hop(df.copy())
    # Turn kg/L to mg/L
    df_scaled["hop_amount"] = df_scaled["hop_amount"] * 1000 * 1000 

    df_scaled["boil_time_factor"] = (1 - math.e ** (-0.04 * df_scaled["hop_time"])) / 4.15
    bigness_factor = 1.65 * 0.000125 ** (gravity_kettle_sg(df.copy())- 1)
    df_scaled["utilization"] = df_scaled["boil_time_factor"] * bigness_factor
    df_scaled["ibu"] = df_scaled["utilization"] * df_scaled["hop_amount"]

    return df_scaled["ibu"].sum() 


def gravity_kettle_sg(df):
    """
    (DataFrame) -> float
    Take the ingredient DataFrame joined to the core DataFrame for a recipe.
    Return the kettle full gravity of the recipe, in SG (eg. 1.050).
    """
    # scale_ferm replaces ferm_amount 
    # from amount of grain in kg
    # to the gravity contribution, in g/L, per fermentable
    return 1 + 0.10 * 4 * scale_ferm(df.copy())["ferm_amount"].sum()  


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
