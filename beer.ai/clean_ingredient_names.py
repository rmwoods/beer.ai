import argparse
import difflib
import pandas as pd
import pickle


# Categories to play the game with
VALID_CATEGORIES = [
    "ferm",
    "hop",
    "yeast",
    "misc",
]


def load_map(fname):
    """Given a fname (pickle), load in the map."""
    try:
        with open(fname, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        print("No previous map found. Starting from scratch.")
        return {}


def check_ingred_name(ingred_name):
    """Given an ingredient name, check if user is happy with it. If not, ask
    for a new string."""

    prompt = f'Searching for similar names to {ingred_name}. Would you like to rename (y/n)?'
    rename = input(prompt)
    ingred_name = input("Enter new name: ")
    print(f"Proceeding with {ingred_name}.")
    return ingred_name


def clean_ingredients(ingred_path, category):
    """Go through unique ingredients and find similar strings. Map from similar
    cases to 'standard' name. Save results in a dict, written to a pickle."""

    with pd.HDFStore(ingred_path, "r") as store:
        # Just work on subset for testing
        df = store.select("ingredients", where="index < 100")

    col = category + "_name"
    out_name = f"{category}map.pickle"

    ingred_map = load_map(out_name)

    # Get the subset of ingred_name to be cleaned
    ingred_names_to_clean = df.loc[~df[col].isin(ingred_map.keys()), col]

    # Get the most common unique name remaining
    ingred_names = ingred_names_to_clean.value_counts()

    for ingred_name in ingred_names.index:

        ingred_name = check_ingred_name(ingred_name)

        # Suggest similar names
        ingred_name_similar = difflib.get_close_matches(
                                ingred_name,
                                ingred_names_to_clean.astype('str').unique(),
                                n=10000,
                                cutoff=0.6
                              )

        # Play the matching game
        for item in ingred_name_similar:
            prompting = True
            while prompting:
                prompt = f'Category:\n{ingred_name}. Does this belong?\n-------------'
                print(prompt)
                belong = input(f'{item}: (y/n)? ')
                if belong == 'y':
                    ingred_map[item] = ingred_name
                    print('Accepted')
                    prompting = False
                elif belong == 'n':
                    print('Rejected')
                    prompting = False
                else:
                    print('Invalid input. Try again.')
                    prompting = True

        # Save the dictionary
        print(f"Writing key/vals for {ingred_name}.")
        with open(f"{category}map.pickle", "wb") as f:
            pickle.dump(ingred_map, f)


def make_arg_parser():
    """Create and return argument parser."""

    parser = argparse.ArgumentParser(
        description="Script to run through beer data and map differently spelled "
            "or referenced ingredients to a standard name."
    )

    parser.add_argument(
        "-f",
        "--filename",
        default="all_recipes.h5",
        help="path of HDF file containing ingredients. Default is "
            "'all_recipes.h5' in current directory."
    )
    parser.add_argument(
        "-c",
        "--category",
        choices=VALID_CATEGORIES,
        default="ferm",
        help="Which ingredient category to play the game with."
    )
    return parser


if __name__ == "__main__":
    parser = make_arg_parser()
    args = parser.parse_args()
    clean_ingredients(args.filename, args.category)
