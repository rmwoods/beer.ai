import json
import numpy as np


def get_style_guide():
    with open("styleguide.json") as f:
        return json.load(f)


def scale_ferm(df, scale_volume="boil_size"):
    """
    Scale the fermentables by the boil size (accounting for yield).
    
        scaled = `ferm_amount` * `efficiency` / `boil_size`

    Parameters
    ==========
    df: DataFrame
        A dataframe containing, at minimum, "ferm_amount", "efficiency", and
        "boil_size".
    scale_volume: str, default "boil_size"
        The volume to use to scale the fermentable quantity.
    
    Return:
    =======
    Series that represents the scaled fermentables in units of kg/L extract in the boil kettle.
    """
    scaled_ferm = df["ferm_amount"] / df[scale_volume]
    scaled_ferm = scaled_ferm.replace([np.inf, -np.inf], np.nan)
    return scaled_ferm


def scale_hop(df, scale_volume_dry="batch_size", scale_volume_boil="boil_size"):
    """
    Compute the scaled hop quantities.

        Dry hopping:
            scaled = hop_amount / scale_volume 

        All other (most commonly boil):
            scaled = hop_amount * hop_alpha * (1 - 0.1 * (hop_form == "leaf")) / scale_volume 

        Where scale_volume can be the volume of the batch or boil.    

    Parameters
    ==========
    df: DataFrame
        A dataframe containing, at minimum, `hop_amount`, `hop_use`,
        `hop_alpha`, `hop_form`, `boil_size`, and `batch_size`.
    scale_volume_dry: str, default "batch_size"
        The volume to use to scale the hop quantity for dry hops.
    scale_volume_boil: str, default "boil_size"
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
    dry_scaled = df.loc[dh_cond, "hop_amount"] / df.loc[dh_cond, scale_volume_dry]

    # Every other hop use
    bh_cond = df["hop_use"] != "dry hop"
    boil_scaled = (
        df.loc[bh_cond, "hop_amount"]
        * df.loc[bh_cond, "hop_alpha"]
        * (1 - 0.1 * (df.loc[bh_cond, "hop_form"] == "leaf").astype(int))
        / df.loc[bh_cond, scale_volume_boil]
    )
    scaled = dry_scaled.append(boil_scaled).sort_index()
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
    Return a Series with 1's matching the indices of df. This is considered scaled for yeast
    since `yeast_amount` is not typically given.

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
    Series representing estimate of IBU for the given recipes.
    """
    # if hops_col not in df.columns:
    #    scale_hop(df, hop_col)
    # Get rid of dry hops
    sub_df = df.loc[df["hop_use"] != "dry hop"]
    # Turn kg/L to mg/L
    hop_amount = sub_df[hop_col] * 1000 * 1000

    boil_time_factor = (1 - np.exp(-0.04 * sub_df["hop_time"])) / 4.15
    bigness_factor = 1.65 * 0.000125 ** (gravity_kettle_sg(df) - 1)
    utilization = boil_time_factor * bigness_factor
    ibu = utilization * hop_amount
    ibu = ibu.groupby(ibu.index).sum()
    return ibu


def gravity_kettle_sg(df, ferm_col="ferm_amount"):
    """
    Return the wort gravity at the beginning of the boil, in S.G.

    wort gravity = sum of (gravity contributions of each fermentable)
    Where, for a fermentable:
        gravity contribution (ºPlato) = 
            mass * yield * efficiency / kettle volume 
    And:
        S.G. = 1 + 0.004 * ºPlato

    Parameters
    ==========
    df: DataFrame
        A DataFrame containing, at minimum:
            "ferm_yield", "efficiency", ferm_col 
        Where: 
            "ferm_amount" is scaled
    ferm_col: str, default "ferm_amount"
        The name of the column containing scaled fermentable quantities.

    Return
    ======
    Series representing wort gravity for each recipe.
    """

    # ferm_extract_yield
    fey = df[ferm_col] * df["ferm_yield"] * df["efficiency"]
    return 1 + 0.004 * fey.groupby(fey.index).sum()


def gravity_original_sg(df, boiloff=0.10, ferm_col="ferm_amount"):
    """
    Calculate the original gravity of the recipe, in SG.

    original gravity = kettle full gravity * (1 - boiloff * boil time / 60 minutes)

    Where: 
        kettle full gravity is the gravity at the end of the lauter, before boil, in S.G.
        boiloff is the % of volume lost to evaporation, per hour
        boil time is the duration of the boil, in minutes

    Parameters
    ==========
    df: DataFrame
        A DataFrame containing, at minimum:
            "boil_time", "ferm_yield", "efficiency", ferm_col 
        Where: 
            "ferm_amount" is scaled
    boiloff: float, default 0.10
        The % of the kettle full volume lost per 60 minutes.
    ferm_col: str, default "ferm_amount"
        The name of the column containing scaled fermentable quantities.

    Return
    ======
    Series representing the original gravity for each recipe.
    """
    gravity_kettle = gravity_kettle_sg(df, ferm_col)
    boil_time = df["boil_time"].groupby(df.index).first()
    return gravity_kettle * (1 - boiloff * boil_time / 60)


def gravity_final_sg(df, ferm_col="ferm_amount"):
    """
    Calculate the final gravity of the recipe, in SG.

    final gravity = (original gravity - 1) * attenuation + 1

    Where: 
        original gravity is the gravity before fermentation, in SG 
        attenuation is the apparent fraction of extract removed by fermentation

    Parameters
    ==========
    df: DataFrame
        A DataFrame containing, at minimum:
            "yeast_attenuation", "boil_time", "ferm_yield", "efficiency", ferm_col 
        Where: 
            "ferm_amount" is scaled
    boiloff: float, default 0.10
        The % of the kettle full volume lost per 60 minutes.
    ferm_col: str, default "ferm_amount"
        The name of the column containing scaled fermentable quantities.

    Return
    ======
    Series representing the original gravity for each recipe.
    """
    gravity_kettle = gravity_kettle_sg(df, ferm_col)
    atten = df["yeast_attenuation"].groupby(df.index).mean() + 1
    return (gravity_original_sg(df) - 1) * atten + 1


def srm(df, ferm_col="ferm_amount"):
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

    Return:
    =======
    Series representing estimate of the SRM for the given recipes.
    """
    # ferm_amount in kg, boil_size in kg
    kg_to_lb = 2.20462
    l_to_gal = 0.264172

    mcu = df["ferm_color"] * df[ferm_col] * kg_to_lb / l_to_gal
    srm = 1.4922 * mcu.groupby(mcu.index).sum() ** 0.6859
    return srm


def color(*args, **kwargs):
    """This is a convenience function, see `srm()` for documentation."""
    return srm(*args, **kwargs)


def abv(df, ferm_col="ferm_amount"):
    """Return ABV (Alcohol By Volume) for a recipe.
    Use the following formulae:
    (Source: "Brewing Calculations" by Jim Helmke, D.G. Yuengling & Son
    MBAA Brewing and Malting Science Course, Fall 2016, Madison)

        ABV = 1.25 * ABW
        ABW = 0.42 * (OE - attenuation * OE)
        OE is determined by solving the quadratic:
            extract = OE * (1 + 0.004 * OE)

        Where:
            OE (original extract) is in degrees Plato
            attenuation is a %
            extract is in kg/hL = 0.01 * (kg/L)

    Parameters:
    ===========
    df: Pandas DataFrame
        DataFrame containing scaled fermentable quantities and yeast
        attenuations. Assumed to have "yeast_attenuation" column as well as
        `ferm_col` column. The `ferm_col` is the **scaled** fermentable
        quantities.

    Return:
    =======
    Series representing estimate of the ABV for the recipes.
    """

    # gb = df.groupby(df.index)
    # OE = np.roots([0.004, 1, -gb[ferm_col].sum().values])
    # ABW = 0.42 * (OE - gb["yeast_attentuation"].mean() * OE)
    # ABV = pd.Series(1.25 * ABW, index=ABW.index, name="abv")
    # return df.merge(ABV, left_index=True, right_index=True, how="left")

    og = gravity_original_sg(df)
    fg = gravity_final_sg(df)
    abv = ((1.05 * (og - fg)) / fg) / 0.79 * 100.0
    return abv
