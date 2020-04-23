import json
import numpy as np
import pandas as pd


def get_style_guide():
    with open("styleguide.json") as f:
        return json.load(f)


def scale_ferm(df, scale_volume="batch_size"):
    """
    Scale the fermentables by a volume measure. 

        scaled = `ferm_amount` / scale_volume

    Parameters
    ==========
    df: DataFrame
        A dataframe containing, at minimum:
            "ferm_amount",
            scale_volume
    scale_volume: str, default "batch_size"
        The column containing the volume to use to scale the fermentable quantity.

    Return:
    =======
    Series representing the scaled fermentables, in units of kg/L.
    """
    scaled_ferm = df["ferm_amount"] / df[scale_volume]
    scaled_ferm = scaled_ferm.replace([np.inf, -np.inf], np.nan)
    return scaled_ferm


def scale_hop(df, scale_volume_dry="batch_size", scale_volume_boil="batch_size"):
    """
    Compute the scaled hop quantities.

        Dry hopping:
            scaled = hop_amount / scale_volume

        All other (most commonly boil):
            scaled = hop_amount * hop_alpha * (1 - 0.1 * (hop_form == "leaf")) / scale_volume

        Where scale_volume can be the volume of either the batch or boil.

    Parameters
    ==========
    df: DataFrame
        A dataframe containing, at minimum, `hop_amount`, `hop_use`,
        `hop_alpha`, `hop_form`, `boil_size`, and `batch_size`.
    scale_volume_dry: str, default "batch_size"
        The volume to use to scale the hop quantity for dry hops.
    scale_volume_boil: str, default "batch_size"
        The volume to use to scale the hop quantity for kettle hops.

    Return:
    =======
    Series representing the scaled hops in units of kg/L extract in the boil
    kettle.


    NOTE:
        The scaled hop quantities will differ depending on the `hop_use`
        column.
        `hop_use` == "dry hop"
            Calculate scaled hops as the kilograms of dry hops per liter by
            dividing by scale_volume_dry
        `hop_use` != "dry hop" (all other categories)
            Calculate scaled hops as the kilograms of alpha acids per
            scale_volume_boil. This calculation differentiates between
            `hop_form` == "leaf" and `hop_form` != "leaf".
    """
    # Dry hops
    dh_cond = df["hop_use"] == "dry hop"
    dh_inds = np.where(dh_cond)[0]
    dry_scaled = df.loc[dh_cond, "hop_amount"] / df.loc[dh_cond, scale_volume_dry]
    # Set to numerical index for appending to keep order
    dry_scaled.index = dh_inds

    # Every other hop use
    bh_cond = df["hop_use"] != "dry hop"
    bh_inds = np.where(bh_cond)[0]
    boil_scaled = (
        df.loc[bh_cond, "hop_amount"]
        * df.loc[bh_cond, "hop_alpha"]
        * (1 - 0.1 * (df.loc[bh_cond, "hop_form"] == "leaf").astype(int))
        / df.loc[bh_cond, scale_volume_boil]
    )
    # Set to numerical index for appending to keep order
    boil_scaled.index = bh_inds
    scaled = dry_scaled.append(boil_scaled).sort_index()
    # Reset to original index
    scaled.index = df.index
    scaled = scaled.replace([np.inf, -np.inf], np.nan)
    return scaled


def scale_misc(df, scale_volume="batch_size"):
    """
    Scale the miscellaneous quantities by the batch size.

        scaled = `misc_amount` / `batch_size`

    Parameters
    ==========
    df: DataFrame
        A dataframe containing, at minimum, "misc_amount" and "batch_size".
    scale_volume: str, default "batch_size"
        The volume to use to scale the misc quantity.


    Return:
    =======
    Series representing the scaled miscellaneous ingredients in units of kg/L
    in the batch kettle.
    """
    misc_scaled = df["misc_amount"] / df[scale_volume]
    misc_scaled = misc_scaled.replace([np.inf, -np.inf], np.nan)
    return misc_scaled


def scale_yeast(df):
    """
    Return a Series with 1's matching the indices of df. This is considered
    scaled for yeast since `yeast_amount` is not typically given.

    Parameters
    ==========
    df: DataFrame
        A dataframe containing, at minimum, "misc_amount" and "batch_size".

    Return:
    =======
    Series representing the scaled yeast. This value has no units.
    """
    inds = df.loc[~df["yeast_name"].isna()].index
    return pd.Series(np.ones(len(inds), index=inds))


def ibu(df, hop_col="hop_scaled", pbg_col="pbg", utilization_factor=4.15):
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
    df: Pandas DataFrame
        Dataframe containing scaled hop quantities and addition times.
        Dataframe assumed to have "hop_time" as a column, which represents the
        duration of boil following hop addition in minutes.
    hop_col: str, default "hop_scaled"
        Name of column containing scaled hop quantities.
    pbg_col: str, default "pbg"
        Name of column containing pre-boil gravity (kettle gravity). If this
        column does not exist, it is calculated using `gravity_kettle()`.
    utilization_factor: float, default 4.15
        Value used to normalize boil time factor. Tinseth uses 4.15, but
        comments that this is an adjustable parameter. For example, it looks
        like Brewer's Friend might use 3.75.

    Return:
    =======
    Series representing estimate of IBU for the given recipes.
    """
    # Get rid of dry hops
    sub_df = df.loc[df["hop_use"] != "dry hop"]
    # Turn kg/L to mg/L
    hop_amount = sub_df[hop_col] * 1000 * 1000

    if pbg_col in df.columns:
        pbg = sub_df[pbg_col]
    else:
        pbg = gravity_kettle(sub_df)

    boil_time_factor = (1 - np.exp(-0.04 * sub_df["hop_time"])) / utilization_factor
    bigness_factor = 1.65 * 0.000125 ** (pbg - 1)
    utilization = boil_time_factor * bigness_factor
    ibu = utilization * hop_amount
    ibu = ibu.groupby(ibu.index).sum()
    return ibu


def gravity_wort(df, scale_volume="batch_size", moisture_factor=0.96):
    """
    Return the wort gravity, either:
        Kettle gravity
            Before the boil, if scale_volume is "boil_size"
        Original gravity
            Before the fermentation, if scale_volume is "batch_size"

    wort gravity = sum of (gravity contributions of each fermentable)
    Where, for a fermentable:
        gravity contribution (ºPlato) =
            mass * yield * moisture correction * efficiency / volume
    And:
        S.G. = 1 + 0.004 * ºPlato
        And moisture correction = 0.96

    Scaling the fermentable accounts for the ratio of mass and volume.

    Parameters
    ==========
    df: DataFrame
        A DataFrame containing, at minimum:
            "ferm_amount", "ferm_yield", "efficiency", scale_volume
    scale_volume: str, default "batch_size"
        The name of the column containing the volume to use to scale the
        fermentable quantities.
    moisture_factor: float, default 0.96
        Factor to account for the moisture in fermentables (0.96 implies 4%
        moisture in the fermentable).

    Return
    ======
    Series representing wort gravity for each recipe.
    """
    ferm_scaled = scale_ferm(df, scale_volume)

    # ferm_extract_yield
    # Multiply by 100 to get from fraction to plato (which is percentage)
    fey = ferm_scaled * df["ferm_yield"] * df["efficiency"] * moisture_factor * 100
    return 1 + 0.004 * fey.groupby(fey.index).sum()


def gravity_kettle(df, *args, **kwargs):
    """
    This is a convenience function to calculate pre-boil wort gravity.
    See gravity_wort() for documentation.
    """
    return gravity_wort(df, *args, scale_volume="boil_size", **kwargs)


def gravity_original(df, *args, **kwargs):
    """
    This is a convenience function to calculate pre-fermentation wort gravity.
    See gravity_wort() for documentation.
    """
    return gravity_wort(df, *args, scale_volume="batch_size", **kwargs)


def gravity_final(df, og_col="og"):
    """
    Calculate the final gravity of the recipe, in SG.

    final gravity = (original gravity - 1) * (1 - attenuation) + 1

    Where:
        original gravity is the gravity before fermentation, in SG
        attenuation is the apparent fraction of extract removed by fermentation

    Parameters
    ==========
    df: DataFrame
        A DataFrame optionally containing og_col.
    og_col: str, default "og"   
        Column in df containing the original gravity of the recipes.
        If og_col is not in df, calculate it by calling `original_gravity()`
        (which has its own requirements)

    Return
    ======
    Series representing the original gravity for each recipe.
    """
    if og_col not in df.columns:
        og = gravity_original(df)
    else:
        og = df[og_col]

    # Attenuation is in percent, not fraction. Divide by 100 to get to fraction
    atten = df["yeast_attenuation"].groupby(df.index).mean() / 100
    return (og - 1) * (1 - atten) + 1


def srm(df, ferm_col="ferm_scaled"):
    """Return SRM (Standard Reference Method units), a measure of colour, for a
    recipe.
    Use the Morey formula:
    (Source: https://web.archive.org/web/20100402141609/http://www.brewingtechniques.com/brewingtechniques/beerslaw/morey.html)

        SRM = 1.4922 * (sum of MCU over the grain bill) ^ 0.6859
        MCU =  grain color * grain weight / kettle volume

        Where:
            grain color is in °L (degrees Lovibond)
            grain weight is in lbs
            kettle volume is in gallons

    Parameters:
    ===========
    df: Pandas DataFrame
        DataFrame containing scaled fermentable quantities and fermentable
        colors. Assumed column is "ferm_color".
    ferm_col: str, default "ferm_scaled"
        Name of column in df containing scaled fermentables

    Return:
    =======
    Series representing estimate of the SRM for the given recipes.
    """
    # ferm_amount in kg, boil_size in kg
    kg_to_lb = 2.20462
    l_to_gal = 0.264172

    if ferm_col in df.columns:
        ferm_scaled = df[ferm_col]
    else:
        ferm_scaled = scale_ferm(df)

    # malt color units
    mcu = df["ferm_color"] * df[ferm_col] * kg_to_lb / l_to_gal
    srm = 1.4922 * mcu.groupby(mcu.index).sum() ** 0.6859
    return srm


def color(*args, **kwargs):
    """This is a convenience function, see `srm()` for documentation."""
    return srm(*args, **kwargs)


def abv(df, ferm_col="ferm_scaled", og_col="og", fg_col="fg"):
    """Return ABV (Alcohol By Volume) for a recipe.
    Formula:
        abv = ((1.05 * (og - fg)) / fg) / 0.79 * 100.0
        Source: TBD

        Where:
            og is the original gravity, in SG
            fg is the final gravity, in SG

    Parameters:
    ===========
    df: Pandas DataFrame
        DataFrame containing scaled fermentable quantities and yeast
        attenuations. Assumed to contain og_col, fg_col as columns, though if
        it does not, it calculates them.
    og_col: str, default "og"
        Name of column in df containing original gravity values. If this column
        does not exist in df, it will be obtained by calling
        `gravity_original()` (which has its own requirements - see docstring).
    fg_col: str, default "fg"
        Name of column in df containing final gravity values. If this column
        does not exist in df, it will be obtained by calling `gravity_final()`
        (which has its own requirements - see docstring).
    ferm_col: str, default "ferm_scaled"
        Name of column in df containing scaled fermentable quantities. Only
        used if og_col or fg_col are not in df (passed through to
        gravity_original/final functions).

    Return:
    =======
    Series representing estimate of the ABV for the recipes.
    """

    if og_col not in df.columns:
        og = gravity_original(df, ferm_col=ferm_col)
    else:
        og = df[og_col]

    if fg_col not in df.columns:
        fg = gravity_final(df, ferm_col=ferm_col)
    else:
        fg = df[fg_col]

    return ((1.05 * (og - fg)) / fg) / 0.79 * 100.0
