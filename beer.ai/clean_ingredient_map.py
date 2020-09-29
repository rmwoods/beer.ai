import csv
import os
import pickle

VALID_CATEGORIES = ["ferm", "hop", "yeast", "misc"]


def load_map(map_category):
    """Return a dictionary containing an ingredient map from clean_ingredient_names.py"""
    if map_category not in VALID_CATEGORIES:
        print("Category is not valid.")
        return {}

    fname = f"{map_category}map.pickle"
    try:
        f = open(fname, "rb")
        d = pickle.load(f)
        print(f"Loaded {fname} map. Contains {len(d)} keys.")
        return d
    except FileNotFoundError:
        print("File not found.")
        return {}


def show_ingred(d):
    """Display the unique ingredients in the map."""
    s = set(val for val in d.values())
    print(*sorted(s), sep="\n")


def show_ingred_cont(d, substr):
    """Display the unique ingredients in the map whose name contains a substring."""
    s = set(val for val in d.values() if substr in val)
    print(*sorted(s), sep="\n")


def show_ingred_cleaned(d, ingred):
    """Display the list of ingredients that have been mapped to a single target ingredient."""
    l = [k for k in d.keys() if d[k] == ingred]
    print(*l, sep="\n")


def rename_ingred(d, ingred_to_rename, ingred_target):
    """Rename the first ingredient as the second.
    The keys that used to have the value (ingred_to_rename) will now have the value (ingred_target)."""
    for k in d.keys():
        if d[k] == ingred_to_rename:
            d[k] = ingred_target
            print(f"Re-mapped {k} from {ingred_to_rename} to {d[k]}.")


def remap_ingred(d, ingred_to_remap, ingred_target):
    """Re-map a key to a new value. Kick an ingredient out of a category and put it in a new one."""
    original_value = d[ingred_to_remap]
    d[ingred_to_remap] = ingred_target
    print(f"Re-mapped {ingred_to_remap} from {original_value} to {d[ingred_to_remap]}.")


def ingred_to_csv(d, name):
    """Save the list of unique values (target ingredients) as a CSV whose name is {name}.csv."""
    unique_values = set(val for val in d.values())
    unique_values_list = sorted(unique_values)

    fname = f"{name}.csv"

    with open(fname, "w") as f:
        out = csv.writer(f, delimiter=",", quoting=csv.QUOTE_ALL)
        for row in zip(unique_values_list):
            out.writerow(row)

    print(f"Saved the list of unique ingredients as {fname}.")


def save_map(d, map_category, *suffix):
    """Save the map in a new pickle, with an optional suffix. Don't over-write an existing map."""
    if map_category not in VALID_CATEGORIES:
        print("Category is not valid.")
        return {}

    if suffix:
        suffix_str = suffix[0]
    else:
        suffix_str = ""

    fname = f"{map_category}map_{suffix_str}.pickle"
    if os.path.exists(fname):
        print(
            f"a file named {fname} already exists! Map not saved. Add a suffix to make a unique filename."
        )
    else:
        f = open(fname, "wb")
        pickle.dump(d, f)
        print(f"Map saved as {fname}.")
