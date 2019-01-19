import argparse
from cmd import Cmd
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


class Cleaner(Cmd(completekey=None)):
    """Program for interacting with and cleaning ingredients."""

    intro = "Welcome to the ingredient cleaner! Type ? to list commands.\n"
    prompt = "cleaner> "

    hdf_path = "all_recipes.h5"
    category = None
    hdf_col = None
    map_name = None
    ingred_map = None
    cur_ingred_name = None
    ingred_name_similar = []
    df = None

    record_file = None

    # ----- basic commands -----
    def do_set_category(self, arg):
        f"""Set the category to be mapped. Acceptable values are {VALID_CATEGORIES}."""
        category = arg
        if category not in VALID_CATEGORIES:
            print("Invalid category")
            return
        self.map_name = f"{arg}map.pickle"
        self.ingred_map = load_map(map_name)
        self.hdf_col = arg + "_name"

        # XXX - update the number below to be a passed in parameter
        with pd.HDFStore(self.hdf_path, "r") as store:
            self.df = store.select("ingredients", where="index < 10000", columns=[sef.hdf_col])

    def do_map(self, arg):
        """Begin the process of finding similar strings to the top unmapped ingredient."""
        # Get the subset of ingred_name to be cleaned
        ingred_names_to_clean = self.df.loc[~self.df[col].isin(self.ingred_map.keys()), self.hdf_col]

        # Get the most common unique name remaining
        try:
            self.cur_ingred_name = ingred_names_to_clean.value_counts().index[0]
        except IndexError:
            print(f"No {self.category}'s left to map (or none found in current df).")
            return

        print("Mapping {self.category}'s similar to {self.cur_ingred_name}")

        # Suggest similar names
        self.ingred_name_similar = difflib.get_close_matches(
                                self.cur_ingred_name,
                                ingred_names_to_clean.astype('str').unique(),
                                n=10000,
                                cutoff=0.6
                              )
        # XXX - loop over ingred_name_similar here? Add commands for it?

    def do_next(self, arg):
        """Go to the next ingredient group to map."""
        pass

    # ----- boilerplate stuff ----
    def do_exit(self, arg):
        print("Bye.")
        return True

    def help_exit(self):
        print("Exit the application. Shorthand: x q Ctrl-D.")

    def default(self, arg):
        if arg == 'x' or arg == 'q':
            return self.do_exit(arg)
    
    # ----- record and playback -----
    def do_record(self, arg):
        '''Save future commands to filename:  RECORD blah.cmd'''
        self.record_file = open(arg, 'w')

    def do_playback(self, arg):
        '''Playback commands from a file:  PLAYBACK blah.cmd'''
        self.close()
        with open(arg) as f:
            self.cmdqueue.extend(f.read().splitlines())

    def precmd(self, line):
        line = line.lower()
        if self.record_file and 'playback' not in line:
            print(line, file=self.file)
        return line

    def close(self):
        if self.record_file:
            self.record_file.close()
            self.record_file = None

    do_EOF = do_exit
    help_EOF = help_exit


def load_map(fname):
    """Given a fname (pickle), load in the map."""
    try:
        with open(fname, "rb") as f:
            d = pickle.load(f)
            print("Loaded {fname}. Contains {len(d)} keys.")
            return d
    except FileNotFoundError:
        print("No previous map found. Starting from scratch.")
        return {}


def clean_ingredients(ingred_path, category):
    """Go through unique ingredients and find similar strings. Map from similar
    cases to 'standard' name. Save results in a dict, written to a pickle."""

    with pd.HDFStore(ingred_path, "r") as store:
        #df = store.select("ingredients")
        # Just work on subset for testing
        df = store.select("ingredients", where="index < 10000")

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
        counter = 0
        for item in ingred_name_similar:
            if item == ingred_name:
                ingred_map[item] = ingred_name
                continue
            prompting = True
            while prompting:
                print('Ingredient names remaining: {}\n'.format(len(ingred_name_similar) - counter))
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
                print('\n\n')
                if not prompting:
                    counter += 1
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
        help="Which ingredient category to play the game with. Default: 'ferm'."
    )
    return parser


if __name__ == "__main__":
    parser = make_arg_parser()
    args = parser.parse_args()
    #clean_ingredients(args.filename, args.category)
    c = Cleaner
    c.cmdloop()

