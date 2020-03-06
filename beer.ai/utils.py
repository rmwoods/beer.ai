import json


def get_style_guide():
    with open("styleguide.json") as f:
        style_guide = json.load(f)


def ibu(df):
    """Return an estimated IBU (International Bitterness Unit) given a beer
    recipe. This is calculated with the following equation:

        FILL IN HERE

    Parameters:
    ===========
    df: Pandas DataFrame
        Dataframe containing scaled hop quantities and addition times.
        Assumed columns are "hop_scaled", "hop_time"

    Return:
    =======
    IBU: float
        Estimate of IBU for the given recipes.
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
