"""
Given a recipe (or recipes), convert the recipe to a vector for use in training
a model.
"""

CORE_COLS = ["batch_size", "boil_size", "boil_time", "efficiency"]
ING_COLS = [
    "ferm_name",
    "ferm_amount",
    "ferm_yield",
    "hop_name",
    "hop_amount",
    "hop_form",
    "hop_use",
    "hop_time",
    "misc_name",
    "misc_use",
    "misc_amount",
    "yeast_name",
]
CATEGORIES = ["ferm", "hop", "yeast", "misc"]



def recipe2vec(recipe):
    """Given a vocabulary and a recipe, convert that recipe to a vector."""
    pass


def recipes2vec(recipes):
    """Given a list of recipes, convert them all to vectors."""
    for rec in recipes:
        recipe2vec(rec)


def scale_ferm(df):
    """
    (DataFrame) -> float
    Compute the scaled fermentable quantity.

    Take as input a subset of the ing DataFrame, joined to the core DataFrame.
    Replace ferm_scaled with the gravity contribution of the fermentable:
        g/L extract in the boil kettle.
    """
    df['ferm_amount'] = df['ferm_amount'] * df['ferm_yield'] * df['efficiency'] / df['boil_size']
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
        * (1 - 0.1 * int(df.loc[bh_cond, "hop_form"] == "leaf")) \
         / df.loc[bh_cond, "boil_size"]
    return df


def scale_misc(df):
    """
    (DataFrame) -> float
    Compute the scaled misc quantity.

    Take as input a subset of the ing DataFrame, joined to the core DataFrame.
    Return a scaled misc quantity.
    """
    df['misc_amount'] = df['misc_amount'] / df['batch_size']


def scale_quantities(df):
    """ Compute scaled ingredient quantities. """
    df = scale_ferm(df)
    df = scale_hops(df)
    df = scale_misc(df)
    return df


def apply_map(df):
    """Given a dataframe with the appropriate columns (specified in CORE_COLS
    and ING_COLS), use the ingredient maps to replace names with standard names
    for use in recipe2vec.
    """
    good = df
    for category in CATEGORIES:
        map_file = f"{category}map.pickle"
        with open(map_file, "rb") as f:
            ing_map = pickle.load(f)
        good = good[good[f"{category}_name"].isin(ing_map.keys())]
        good[f"{category}_name"] = good[f"{category}_name"].replace(ing_map)
    return good


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
            yield df


def main():
    for df in load_data():
        recipes = map_data()
        recipe_vecs = recipes2vec(recipes)
        return recipe_vecs


if __name__ == "__main__":
    # main()
