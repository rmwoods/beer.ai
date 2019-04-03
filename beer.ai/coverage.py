# How many recipes are completely cleaned by our maps?
# Completely cleaned means every ingredient is a key in a map

import pandas as pd
import numpy as np
import pickle

VALID_CATEGORIES = [
    "ferm",
    "hop",
    "yeast",
    "misc",
]

if __name__ == "__main__":
    # Load ingredient DataFrame
    col_names = [f'{cat}_name' for cat in VALID_CATEGORIES]
    with pd.HDFStore("all_recipes.h5") as store:
        df = store.select('ingredients', columns=col_names)

    # Get the set of unique recipe IDs that are completely covered by each map
    maps = {}
    s = set(df.index)
    for cat in VALID_CATEGORIES:
        # Load the map
        fname =  f"{cat}map.pickle"
        try:
            f = open(fname, "rb")
            maps[cat] = pickle.load(f)
            print(f"Loaded {fname} map. Contains {len(maps[cat])} keys.")
            
        except FileNotFoundError:
            print("File not found.")
    
        # Get the recipe IDs covered by the map
        col = '{}_name'.format(cat)
        cur_data = df[col].dropna()
        ingred_in_map = cur_data.isin(maps[cat].keys())
        all_ingred_in_map = ingred_in_map.groupby(cur_data.index).agg(np.all)
        s_cat = set(all_ingred_in_map[all_ingred_in_map].index)
        
        n_mapped_cat = len(s_cat)
        n_total_cat = df.index.max()
        pct_mapped_cat = 100*len(s_cat)/df.index.max()
        print("Coverage: {} out of {} recipes by the {} map. ({:.0f}%)".format(n_mapped_cat, n_total_cat, cat, pct_mapped_cat))
        
        # Add the recipes that are covered by this category, and the previous category, in the map
        s = s.intersection(s_cat)
    
    # Count the number of recipes covered by the map
    n_mapped = len(s)
    n_total = df.index.max()
    pct_mapped = 100*len(s)/df.index.max()
    print("Coverage: {} out of {} recipes by all maps. ({:.0f}%)".format(n_mapped, n_total, pct_mapped))
    
  