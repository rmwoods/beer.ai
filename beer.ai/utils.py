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
    """Return an estimated IBU (International Bitterness Unit) given a beer
    recipe. This is calculated with the following equation:

        FILL IN HERE

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
    """Return the SRM (Standard Reference Method), also known as color, for the
    given recipes. This is calculated using the following formula:

        FILL IN HERE

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
    #self.__doc__ = srm.__doc__??
    return srm(*args, **kwargs)


def abv(df):
    """Return the ABV (Alcohol By Volume) for the given recipes. This is
    calculated using the following formula:

        FILL IN HERE

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
