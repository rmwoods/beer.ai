import argparse
import pandas as pd
import difflib

# Categories to play the game with
VALID_CATEGORIES = [
    "ferm",
    "hop",
    "yeast",
    "misc",
]


def apply_cleaning_dict(x, ingred_name_clean_dict):
    """ (str, dict) -> str
    Take:   an entry from the 'ingred_name' column
            a dictionary whose keys are ingred_name entries and whose values are cleaned ingred_name entries
    Return an entry for the 'ingred_name_cleaned column"""
    if x in ingred_name_clean_dict.keys():
        return ingred_name_clean_dict[x]
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


def main(ingred_path, category):
    # Load the ingredients DataFrame
    #ingred_path = r'C:\Users\rwelch\Documents\GitHub\beer.ai\beer.ai\all_recipes.h5'

    store = pd.HDFStore(ingred_path, "r")
    # Just work on subset for testing
    df = store.select("ingredients", where="index < 10000")
    col = category + "_name"
    col_clean = col + "_clean"

    # If it doesn't exist, create a ingred_name_clean column
    if col_clean not in df.columns:
        df[col_clean] = ""


    # ITERATE

    # Open the mapping dictionary
    # Open the (in progress?) dataframe

    # Get the subset of ingred_name to be cleaned
    ingred_name_to_clean = df[col][df[col_clean].isnull()]

    # Get the most common unique name remaining
    ingred_name_category = ingred_name_to_clean.value_counts().index[0]

    # Suggest similar names
    ingred_name_similar = difflib.get_close_matches(ingred_name_category, ingred_name_to_clean.astype('str').unique(), n=10000, cutoff=0.6)

    # Play the ingred game

    for item in ingred_name_similar:
        prompting = 1
        while prompting == 1:

            prompt = f'Category:\n{ingred_name_category}. Does this belong?\n-------------\n{item}'
            print(prompt)
            belong = input('y/n')
            if belong == 'y':
                ingred_name_clean_dict[item] = ingred_name_category
                print('Accepted')
                prompting = 0
            elif belong == 'n':
                print('Rejected')
                prompting = 0
            else:
                print('Invalid input. Try again.')
                prompting = 1

    # Apply the cleaning dict
    # Add the new, cleaned ingredient names to the cleaned column
    df['ferm_name_clean'] = df['ferm_name'].apply(lambda x: apply_cleaning_dict(x, ingred_name_clean_dict))

    # STEPS TO ITERATE
    # DONE Get list of names to be cleaned
    # DONE   In ferm_name, not ferm_name_clean
    # DONE Turn into a unique list of names
    # DONE Pick the unique name that's the most common
    # DONE That's the category. Generate similarity groups for it

    # FUN GAME
    #   For each item in the similarity group, ask
    #   "Same as category name"?
    #       If yes, put it in the dictionary as key whose value is the item
    #       If not, don't do anything

    # When the similarity group game is done, populate ferm_name_clean by:
    #   For ferm_name entries that are keys of the dictionary,
    #      Enter the dictionary value in ferm_name_clean

    # Save the dictionary
    # Save the dataframe


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
