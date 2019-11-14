"""
Given a recipe (or recipes), convert the recipe to a vector for use in training
a model.
"""

import numpy as np
import pandas as pd
import pickle


CORE_COLS = ["batch_size", "boil_size", "boil_time", "efficiency"]
ING_COLS = [
    "ferm_name",
    "ferm_amount",
    "ferm_yield",
    "hop_name",
    "hop_amount",
    "hop_form",
    "hop_alpha",
    "hop_use",
    "hop_time",
    "misc_name",
    "misc_use",
    "misc_amount",
    "yeast_name",
]
CATEGORIES = ["ferm", "hop", "yeast", "misc"]
VOCAB_FILE = "vocab.pickle"
# Number of extra features to add to vector representing non-ingredients, e.g. boil_time
N_EXTRA_FEATURES = 1

with open(VOCAB_FILE, "rb") as f:
    ING2INT = pickle.load(f)
    INT2ING = {v:k for k,v in ING2INT.items()}


def recipes2vec(recipes):
    """Given a list of recipes, convert them all to vectors."""
    data = np.zeros((len(recipes), len(ING2INT) + N_EXTRA_FEATURES))
    name_cols = [cat + "_name" for cat in CATEGORIES]
    amount_cols = [cat + "_amount" for cat in CATEGORIES]

    # Turn mapped ingredients to their integer labels
    recipes[name_cols] = recipes[name_cols].replace(ING2INT)
    # Separate each column into a Series, so we can concat them all into a vectpr
    list_of_name_cols = []
    list_of_amount_cols = []
    # Drop ingredients that are unmapped, or have no amount
    for name_col, amount_col in zip(name_cols, amount_cols):
        # Make sure both name and amount are NaN when:
        #   The amount is NaN
        #   The name is NaN
        #   The amount is 0 
        recipes.loc[recipes[amount_col].isna(), name_col] = np.nan
        recipes.loc[recipes[name_col].isna(), amount_col] = np.nan
        recipes.loc[recipes[amount_col] == 0, [name_col, amount_col]] = np.nan
        
        list_of_name_cols.append(recipes[name_col].dropna())
        list_of_amount_cols.append(recipes[amount_col].dropna())

    # Concatenate the columns together 
    name_concat = pd.concat(list_of_name_cols)
    amount_concat = pd.concat(list_of_amount_cols)

    assert len(name_concat) == len(amount_concat), "Different number of names and amounts of ingredients"
    # Form our vectors!
    data[name_concat.index.astype(int), name_concat.values.astype(int)] = amount_concat.values

    # Add the last column: boil time
    boil_times = recipes['boil_time']
    boil_times = boil_times.loc[~boil_times.index.duplicated(keep='first')]
    data[boil_times.index.astype(int), -1] = boil_times.values

    return data


def scale_ferm(df):
    """
    (DataFrame) -> float
    Compute the scaled fermentable quantity.

    Take as input a subset of the ing DataFrame, joined to the core DataFrame.
    Replace ferm_scaled with the gravity contribution of the fermentable:
        g/L extract in the boil kettle.
    """
    df["ferm_amount"] = df["ferm_amount"] * df["ferm_yield"] * df["efficiency"] / df["boil_size"]
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
    dh_cond = (df["hop_use"] == "dry hop")
    df.loc[dh_cond, "hop_amount"] = df.loc[dh_cond, "hop_amount"] / df.loc[dh_cond, "batch_size"]

    # Every other hop use
    bh_cond = (df["hop_use"] != "dry hop")
    df.loc[bh_cond, "hop_amount"]  =\
        df.loc[bh_cond, "hop_amount"] \
        * df.loc[bh_cond, "hop_alpha"] \
        * (1 - 0.1 * (df.loc[bh_cond, "hop_form"] == "leaf").astype(int)) \
         / df.loc[bh_cond, "boil_size"]
    df["hop_amount"] = df["hop_amount"].replace([np.inf, -np.inf], np.nan)
    return df


def scale_misc(df):
    """
    (DataFrame) -> float
    Compute the scaled misc quantity.

    Take as input a subset of the ing DataFrame, joined to the core DataFrame.
    Return a scaled misc quantity.
    """
    df['misc_amount'] = df['misc_amount'] / df['batch_size']
    df["misc_amount"] = df["misc_amount"].replace([np.inf, -np.inf], np.nan)
    return df


def scale_yeast(df): 
    """
    (DataFrame) -> DataFrame
    Return a DataFrame with a new column yeast_amount = 1
    """
    df.loc[~df['yeast_name'].isna(), 'yeast_amount'] = 1
    return df


def scale_quantities(df):
    """ Compute scaled ingredient quantities. """
    df = scale_ferm(df)
    df = scale_hop(df)
    df = scale_misc(df)
    df = scale_yeast(df)
    # XXX - check here that we're not dropping ALL rows after the first
    df = df.dropna(how="all", subset=["ferm_amount", "hop_amount", "misc_amount"])
    return df


def apply_map(df):
    """Given a dataframe with the appropriate columns (specified in CORE_COLS
    and ING_COLS), use the ingredient maps to replace names with standard names
    for use in recipe2vec.
    """
    for category in CATEGORIES:
        map_file = f"{category}map.pickle"
        with open(map_file, "rb") as f:
            ing_map = pickle.load(f)
        in_map = df[f"{category}_name"].isin(ing_map.keys())
        df.loc[~in_map, f"{category}_name"] = np.nan
        df.loc[in_map, f"{category}_name"] = df.loc[in_map, f"{category}_name"].replace(ing_map)
    return df


def finalize_names(df):
    """For each ingredient category, change the names to the style that is used
    inside of the vocabulary."""

    for category in CATEGORIES:
        col = f"{category}_name"
        prepend = category + "_"
        nans = df[col].isna()
        df.loc[~nans, col] = prepend + df.loc[~nans, col].astype(str)
        if category == "hop":
            append = (df["hop_use"] == "dry hop")&(~df["hop_name"].isna())
            df.loc[append, col] = df.loc[append, col].astype(str) + "_dry"
    return df


def load_prepare_data(path):
    """Given a path to the all_recipes HDF, load in the data, replace the
    ingredient names with standard names from the ingredient maps and then
    scale quantities to boil/batch sizes as appropriate."""
    with pd.HDFStore(path, "r") as store:
        for core in store.select("/core", columns=CORE_COLS, chunksize=1000):
            i_start = core.index[0]
            i_end = core.index[-1]
            ings = store.select(
                    "ingredients",
                    columns=ING_COLS,
                    where=f"index >= {i_start} and index <= {i_end}",
                    )
            df = core.join(ings)
            df = apply_map(df)
            df = scale_quantities(df)
            df = finalize_names(df)
            yield df


def main():
    recipes = []
    for df in load_prepare_data("all_recipes.h5"):
        recipes.append(recipes2vec(df))
    vecs = pd.concat(recipes)
    vecs.to_hdf("recipe_vecs.h5","vecs")


if __name__ == "__main__":
    main()
