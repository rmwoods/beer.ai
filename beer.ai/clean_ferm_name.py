import pandas as pd
import difflib


def main():
    # Load the ingredients DataFrame
    df = pd.read_hdf('all_recipes.h5', key='ingredients')

    # If it doesn't exist, create a ferm_name_clean column
    if 'ferm_name_clean' not in df:
        df['ferm_name_clean'] = ""

    # ITERATE

    # Open the mapping dictionary
    # Open the (in progress?) dataframe

    # Get the subset of ferm_name to be cleaned
    ferm_name_to_clean = df['ferm_name'][df['ferm_name_clean'] == '']

    # Get the most common unique name remaining
    ferm_name_category = ferm_name_to_clean.value_counts().index[0]

    # Suggest similar names
    ferm_name_similar = difflib.get_close_matches(ferm_name_category, ferm_name_to_clean.astype('str').unique(), n=10000, cutoff=0.6)

    # STEPS TO ITERATE
    # Get list of names to be cleaned
    #   In ferm_name, not ferm_name_clean
    # Turn into a unique list of names
    # Pick the unique name that's the most common
    # That's the category. Generate similarity groups for it

    # FUN GAME
    #   For each item in the similarity group, ask
    #   "Same as category name"?
    #       If yes, put it in the dictionary as key whose value is the item
    #       If not, don't do anything
    #   (Include the trivial one of the category mapping to itself)

    # When the similarity group game is done, populate ferm_name_clean by:
    #   For ferm_name entries that are keys of the dictionary,
    #      Enter the dictionary value in ferm_name_clean

    # Save the dictionary
    # Save the dataframe


if __name__ == "__main__":
    main()
