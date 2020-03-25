import json
import numpy as np


def get_style_guide():
    with open("styleguide.json") as f:
        return json.load(f)


def scale_ferm(df, new_col="ferm_amount"):
    """
    Scale the fermentables by the boil size (accounting for yield). Add the
    results as the column `new_col`.
    
        scaled = `ferm_amount` * `efficiency` / `boil_size`

    Parameters
    ==========
    df: DataFrame
        A dataframe containing, at minimum, "ferm_amount", "efficiency", and
        "boil_size".
    new_col: str, default "ferm_amount"
        Name of the new column to add to the given dataframe to contain the
        scaled fermentable. 
    
    Return:
    =======
    None:
        Add `new_col` to the given dataframe containing the scaled
        fermentables in units of kg/L extract in the boil kettle.
    """
    df[new_col] = df["ferm_amount"] / df["boil_size"]
    df[new_col] = df[new_col].replace([np.inf, -np.inf], np.nan)


def scale_hop(df, new_col="hop_amount"):
    """
    Compute the scaled hop quantities. Add the results as the column `new_col`.
    Use the following equations.

        Dry hopping:
            scaled = hop_amount / batch_size

        All other (most commonly boil):
            scaled = hop_amount * hop_alpha * (1 - 0.1 * (hop_form == "leaf")) / boil_size

    Parameters
    ==========
    df: DataFrame
        A dataframe containing, at minimum, `hop_amount`, `hop_use`,
        `hop_alpha`, `hop_form`, `boil_size`, and `batch_size`.
    new_col: str, default "hop_amount"
        Name of the new column to add to the given dataframe to contain the
        scaled hops. 
    
    Return:
    =======
    None:
        Add `new_col` to the given dataframe containing the scaled
        hops in units of kg/L extract in the boil kettle.
    
    
    NOTE:
        The scaled hop quantities will differ depending on the `hop_use`
        column.
        `hop_use` == "dry hop"
            Calculate scaled hops as the kilograms of dry hops per liter by
            dividing by `batch_size`.
        `hop_use` != "dry hop" (all other categories)
            Calculate scaled hops as the kilograms of alpha acids per liter in
            the boil kettle. This calculation differentiates between
            `hop_form` == "leaf" and `hop_form` != "leaf".
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
    Scale the miscellaneous quantities by the batch size. Add the results as
    the column `new_col`.
    
        scaled = `misc_amount` / `batch_size`

    Parameters
    ==========
    df: DataFrame
        A dataframe containing, at minimum, "misc_amount" and "batch_size".
    new_col: str, default "misc_amount"
        Name of the new column to add to the given dataframe to contain the
        scaled misc ingredients. 
    
    Return:
    =======
    None:
        Add `new_col` to the given dataframe containing the scaled
        miscellaneous ingredients in units of kg/L in the batch kettle.
    """
    df[new_col] = df["misc_amount"] / df["batch_size"]
    df[new_col] = df[new_col].replace([np.inf, -np.inf], np.nan)


def scale_yeast(df, new_col="yeast_amount"):
    """
    Return a DataFrame with  `new_col` = 1. This is considered scaled for yeast
    since `yeast_amount` is not typically given.

    Parameters
    ==========
    df: DataFrame
        A dataframe containing, at minimum, "misc_amount" and "batch_size".
    new_col: str, default "yeast_amount"
        Name of the new column to add to the given dataframe to contain the
        scaled yeast. 
    
    Return:
    =======
    None:
        Add `new_col` to the given dataframe containing the scaled
        yeast. This value has no units.
    """
    df.loc[~df["yeast_name"].isna(), new_col] = 1


def ibu(df, hop_col="hop_amount", new_col="ibu"):
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
    sub_df = df.loc[df["hop_use"] != "dry hop"]
    # Turn kg/L to mg/L
    hop_amount = sub_df[hop_col] * 1000 * 1000

    boil_time_factor = (1 - np.exp(-0.04 * sub_df["hop_time"])) / 4.15
    bigness_factor = 1.65 * 0.000125 ** (gravity_kettle_sg(df) - 1)
    utilization = boil_time_factor * bigness_factor
    ibu = utilization * hop_amount
    ibu = ibu.groupby(ibu.index).sum()
    ibu.name = new_col
    return df.merge(ibu, left_index=True, right_index=True, how="left")


def gravity_kettle_sg(df):
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
        Series representing full gravity for recipes.
    """

    # ferm_extract_yield
    fey = df["ferm_amount"] * df["ferm_yield"] * df["efficiency"]
    return 1 + 0.004 * fey.groupby(fey.index).sum()


def gravity_original_sg(df):
    """ XXX write a better docstring
    Calculate the original gravity of the recipe, in SG."""
    gravity_kettle = gravity_kettle_sg(df)
    # The percent of the volume evapourated during the boil, per hour
    boiloff = 0.10
    boil_time = df["boil_time"].groupby(df.index).first()
    return gravity_kettle * (1 - boiloff * boil_time / 60)


def gravity_final_sg(df):
    """ XXX write a better docstring
    Calculate the final gravity of each recipe, in SG."""
    pass


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
    kg_to_lb = 2.20462
    l_to_gal = 0.264172
    import pdb

    pdb.set_trace()
    mcu = df["ferm_color"] * df[ferm_col] * kg_to_lb / l_to_gal
    srm = 1.4922 * mcu.groupby(mcu.index).sum() ** 0.6859
    srm.name = srm_name
    return df.merge(srm, left_index=True, right_index=True, how="left")


def color(*args, **kwargs):
    """This is a convenience function, see `srm` for documentation.

    NOTE: This function passes `srm_name = "color"` to `srm` unless it has
    already been specified.
    """
    if "srm_name" not in kwargs.keys():
        kwargs.update({"srm_name": "color"})
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
    DataFrame:
        New dataframe containing column "abv", an estimate of the ABV for the
        recipes.
    """

    # XXX - come back to this
    # pybeerxml uses:
    # ((1.05 * (self.og - self.fg)) / self.fg) / 0.79 * 100.0
    gb = df.groupby(df.index)
    OE = np.roots([0.004, 1, -gb[ferm_col].sum().values])
    ABW = 0.42 * (OE - gb["yeast_attentuation"].mean() * OE)
    ABV = pd.Series(1.25 * ABW, index=ABW.index, name="abv")
    return df.merge(ABV, left_index=True, right_index=True, how="left")
