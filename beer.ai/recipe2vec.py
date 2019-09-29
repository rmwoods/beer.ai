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


def scale_ferm():
    pass


def scale_misc():
    pass


def scale_hop(style):
    pass


def scale_quantities(df):
    scale_ferm(df)
    scale_hops(df)
    scale_misc(df)


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
    main()
