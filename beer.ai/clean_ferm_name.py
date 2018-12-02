import pandas as pd
import difflib


def apply_cleaning_dict(x, ferm_name_clean_dict):
    """ (str, dict) -> str
    Take:   an entry from the 'ferm_name' column
            a dictionary whose keys are ferm_name entries and whose values are cleaned ferm_name entries
    Return an entry for the 'ferm_name_cleaned column"""
    if x in ferm_name_clean_dict.keys():
        return ferm_name_clean_dict[x]
    else:
        pass


def matching_game(host, contestants):
    """ (str, list) -> dict

    Prompt the user to select ferm_name entries match a category.
    (Get the studio audience to pick contestants that match the host.)

    Take:   a ferm_name category to find matches for (the host)
            a list of ferm_name entries to match with the category (the contestants)

    Return: a dictionary
                whose keys are the ferm_name entries that match (the contestants that match the host)
                whose values are ferm_name category (the host)
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


def main():
    # Load the ingredients DataFrame
    ingred_path = r'C:\Users\rwelch\Documents\GitHub\beer.ai\beer.ai\all_recipes.h5'

    df = pd.read_hdf(ingred_path, key='ingredients')

    # If it doesn't exist, create a ferm_name_clean column
    if 'ferm_name_clean' not in df:
        df['ferm_name_clean'] = ""


    # ITERATE

    # Open the mapping dictionary
    # Open the (in progress?) dataframe

    # Get the subset of ferm_name to be cleaned
    ferm_name_to_clean = df['ferm_name'][df['ferm_name_clean'].isnull()]

    # Get the most common unique name remaining
    ferm_name_category = ferm_name_to_clean.value_counts().index[0]

    # Suggest similar names
    ferm_name_similar = difflib.get_close_matches(ferm_name_category, ferm_name_to_clean.astype('str').unique(), n=10000, cutoff=0.6)

    # Play the ferm game

    for item in ferm_name_similar:
        prompting = 1
        while prompting == 1:

            prompt = 'Category:\n{}. Does this belong?\n-------------\n{}'.format(ferm_name_category,item)
            print(prompt)
            belong = input('y/n')
            if belong == 'y':
                ferm_name_clean_dict[item] = ferm_name_category
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
    df['ferm_name_clean'] = df['ferm_name'].apply(lambda x: apply_cleaning_dict(x, ferm_name_clean_dict))

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


if __name__ == "__main__":
    main()
