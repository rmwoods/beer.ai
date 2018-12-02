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


def apply_cleaning_dict(x, ingred_map):
    """ (str, dict) -> str
    Take:   an entry from the 'ingred_name' column
            a dictionary whose keys are ingred_name entries and whose values are cleaned ingred_name entries
    Return an entry for the 'ingred_name_cleaned column"""
    if x in ingred_map.keys():
        return ingred_map[x]
    else:
        pass


def matching_game(host, contestants):
    """ (str, list) -> dict

    Prompt the user to select ingred_name entries match a category.
    (Get the studio audience to pick contestants that match the host.)

    Take:   a ingred_name category to find matches for (the host)
            a list of ingred_name entries to match with the category (the contestants)

    Return: a dictionary
                whose keys are the ingred_name entries that match (the contestants that match the host)
                whose values are ingred_name category (the host)
    """
    winners = {}

    for item in contestants:

        airing = 1
        # While the show is still on the air
        while airing == 1:

            # Ask the studio audience if the contestant matches the host
            prompt = 'Category:\n{}. Does this belong?\n-------------\n{}'.format(host, item)
            print(prompt)

            match = input('y/n')
            if match == 'y':
                winners[item] = host
                print('Accepted')
                airing = 0
            elif match == 'n':
                print('Rejected')
                airing = 0
            else:
                print('Invalid input. Try again.')
                airing = 1

    return winners


def load_map(fname):
    """Given a fname (pickle), load in the map."""
    try:
        with open(fname, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        print("No previous map found. Starting from scratch.")
        return {}


def main(ingred_path, category):

    with pd.HDFStore(ingred_path, "r") as store:
        # Just work on subset for testing
        df = store.select("ingredients", where="index < 100")

    col = category + "_name"
    out_name = f"{category}map.pickle"

    ingred_map = load_map(out_name)

    # Get the subset of ingred_name to be cleaned
    ingred_name_to_clean = df.loc[~df[col].isin(ingred_map.keys()), col]

    # Get the most common unique name remaining
    ingred_names = ingred_name_to_clean.value_counts()

    for ingred_name in ingred_names.index:
        # Suggest similar names
        ingred_name_similar = difflib.get_close_matches(
                                ingred_name,
                                ingred_name_to_clean.astype('str').unique(),
                                n=10000,
                                cutoff=0.6
                              )

        # Play the ingred game
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
    main(args.filename, args.category)
