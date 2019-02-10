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

DEFAULT_PROMPT = "cleaner> "
PROMPT_SUFFIX = "? > "
EXIT_COMMANDS = ["q", "x", "quit"]


class Cleaner(Cmd):
    """Program for interacting with and cleaning ingredients."""

    intro = "Welcome to the ingredient cleaner! Type ? to list commands.\n"
    prompt = DEFAULT_PROMPT

    hdf_path = "all_recipes.h5"
    category = None
    hdf_col = ""
    map_name = ""
    ingred_map = {}
    cur_ingred_name = None
    cur_ingred_compare = None
    ingred_names_to_compare = []
    prev_ingreds_compare = []
    # Which index in ingredients are we on?
    df = pd.DataFrame()
    # Are we currently mapping an ingredient?
    active = False

    record_file = None

    #------ Dynamic properties ------
    @property
    def ingred_names_to_clean(self):
        """List of ingredients remaining to map."""
        try:
            return self.df.loc[~self.df[self.hdf_col].isin(self.ingred_map.keys()), self.hdf_col].dropna()
        except KeyError:
            return pd.DataFrame()

    # ----- basic commands -----
    def do_set_cat(self, arg):
        self.category = arg
        """Set the category to be mapped. Acceptable values are {VALID_CATEGORIES}."""
        if self.category not in VALID_CATEGORIES:
            print("Invalid category")
            self.category = None
            return

        self.map_name = f"{arg}map.pickle"
        self.ingred_map = load_map(self.map_name)
        self.hdf_col = arg + "_name"

        self.load_df()
        self.set_cur_ingred()
        self.set_ingred_names_to_compare()

    def help_set_cat(self):
        print(f"Set the category to be mapped. Acceptable values are {VALID_CATEGORIES}.")

    def do_status(self, arg):
        """Print the current status of important variables, maps, etc."""
        if self.category:
            print(f"    Category: {self.category}")
            print(f"    N of ingredients mapped: {len(self.ingred_map.keys())}")
            print(f"    Current ingredient to map: {self.cur_ingred_name}")
            if self.ingred_names_to_compare is not None:
                print(f"    N left to map for current ingredient: {len(self.ingred_names_to_compare)}")
            else:
                print("    No similar names found. Run map to generate similar names.")
        else: 
            print("     No category set. Run set_cat to set a category.")

    def help_status(self):
        print("Print the current status of important variables, maps, etc.")

    def do_print(self, arg):
        """Print a specific variable. Meant for debugging."""
        try:
            print(f"arg: {getattr(self, arg)}.")
        except:
            print(f"Can't find {arg}.")

    def do_remain(self, arg):
        """Print the remaining ingreds_names_similar or ingreds_to_clean"""
        if self.active:
            print(f"    Ingredient names left to compare: {self.ingred_names_to_compare}")
        else:
            unique = self.ingred_names_to_clean.unique()
            print(f"    {len(unique)} unique ingredient names left to clean: {unique}")

    def help_remain(self, arg):
        print("Print the remaining ingreds_names_similar or ingreds_to_map")

    def do_map(self, arg):
        """Begin the process of finding similar strings to the top unmapped ingredient."""

        print(f"Mapping {self.category}s similar to {self.cur_ingred_name}.")
        self.active = True
        self.set_ingred_names_to_compare()
        self.advance_ingred()

    def help_map(self):
        print("Begin the process of finding similar strings to the top unmapped ingredient.")

    def do_y(self, arg):
        """Approve cur_ingred_compare to map to cur_ingred_name and advance
        to the next ingredient."""
        print("Accepted.")
        self.ingred_map[self.cur_ingred_compare] = self.cur_ingred_name
        self.advance_ingred()
        save_map(self.map_name, self.ingred_map)

    def do_n(self, arg):
        """Reject cur_ingred_compare to map to cur_ingred_name. Advance to the
        next ingredient."""
        print("Rejected.")
        self.advance_ingred()

    def do_rename(self, arg):
        """Rename the [current | specific] target ingredient."""
        if arg == "":
            print("Pass string to rename to.")
            return
        for k, v in self.ingred_map.items():
            if v == self.cur_ingred_name:
                self.ingred_map[k] = arg
        self.cur_ingred_name = arg
        self.set_prompt_compare()

    def help_rename(self, arg):
        print("Rename the [current | specific] target ingredient.")

    def do_stop(self, arg):
        """Stop the current mapping."""
        self.active = False
        self.prompt = DEFAULT_PROMPT

    def help_stop(self):
        print("Stop the current mapping.")

    def do_undo(self, arg):
        """Remove the previous mapping and re-try."""
        try:
            del self.ingred_map[self.prev_ingreds_compare[-1]]
        except IndexError:
            print("Nothing to undo.")
            return
        self.cur_ingred_compare = self.prev_ingreds_compare.pop(-1)
        self.set_prompt_compare()

    def help_undo(self):
        print("Remove the previous mapping and re-try.")

    def do_save(self, arg):
        """Save the current map."""
        save_map(self.map_name, self.ingred_map)

    def help_save(self):
        print("Save the current map.")

    def do_exclude(self, arg):
        """In current list of ingredients to compare, exclude all entries that
        contain arg in their name.
        arg can be one string to exclude, or a set of strings separated by commas and spaces 
        """
        exclude_strings = arg.split(', ') 
        for s in exclude_strings: 
            # Print which ingredients are being excluded
            exclude_ingred = [i for i in self.ingred_names_to_compare if s in i]
            print(f"Excluding ingredients: {exclude_ingred}")
            # Exclude them 
            self.ingred_names_to_compare = [i for i in self.ingred_names_to_compare if s not in i]
        if arg in self.cur_ingred_compare:
            self.advance_ingred()

    def help_exclude(self):
        print("In current list of ingredients to compare, exclude all entries "
              "that contain arg in their name.")

    def help_merge(self):
        print("")

    # ----- boilerplate stuff ----
    def do_exit(self, arg):
        print("Goodbye!")
        return True

    def help_exit(self):
        print("Exit the application. Shorthand: x q Ctrl-D.")

    def default(self, arg):
        if arg in EXIT_COMMANDS:
            return self.do_exit(arg)
        else:
            print(f"Unknown command '{arg}'.")
    
    # ----- record and playback -----
    def do_record(self, arg):
        """Save future commands to filename:  RECORD blah.cmd"""
        self.record_file = open(arg, 'w')

    def help_record(self):
        print("Save future commands to filename:  RECORD blah.cmd")

    def do_playback(self, arg):
        """Playback commands from a file:  PLAYBACK blah.cmd"""
        self.close()
        with open(arg) as f:
            self.cmdqueue.extend(f.read().splitlines())

    def help_playback(self):
        print("Playback commands from a file:  PLAYBACK blah.cmd")

    def close(self):
        if self.record_file:
            self.record_file.close()
            self.record_file = None

    # ----- pre/post commands -----

    def precmd(self, line):
        #line = line.lower()
        if self.record_file and 'playback' not in line:
            print(line, file=self.file)
        return line

    # ----- shortcuts -----
    do_EOF = do_exit
    help_EOF = help_exit

    # ----- Helper Functions -----
    def load_df(self):
        """Load the dataframe of global data."""
        # XXX - update the number below to be a passed in parameter
        with pd.HDFStore(self.hdf_path, "r") as store:
            self.df = store.select("ingredients", where="index < 10000", columns=[self.hdf_col])

    def advance_ingred(self):
        """Pop the next ingredient to compare to the current ingredient (if
        available) and update the prompt and active fields."""
        try:
            tmp = self.cur_ingred_compare
            self.cur_ingred_compare = self.ingred_names_to_compare.pop(0)
            self.prev_ingreds_compare.append(tmp)
        except IndexError:
            print(f"Finished mapping for {self.cur_ingred_name}.")
            # Save the map
            save_map(self.map_name, self.ingred_map)
            # Advance the ingredient to map
            self.advance_ingred_target()
        # Update the prompt
        self.set_prompt_compare()

    def advance_ingred_target(self):  
        """After finshing mapping a set of ingredients to the target ingredient, move on to the next target."""
        # Get the new ingredient target
        # self.index += 1
        self.set_ingred_names_to_compare()
        self.set_cur_ingred()
        print(f"Starting mapping for {self.cur_ingred_name}.")

    def set_prompt_compare(self):
        """Set the prompt according to the current ingred_name and
        ingred_compare"""
        self.prompt = self.cur_ingred_name + " == " + self.cur_ingred_compare
        self.prompt += PROMPT_SUFFIX

    def set_cur_ingred(self):
        """Get the next ingredient to map to."""
        # Get the most common unique name remaining
        try:
            # self.cur_ingred_name = self.ingred_names_to_clean.value_counts().index[self.index]
            self.cur_ingred_name = self.ingred_names_to_clean.value_counts().index[0]
        except IndexError:
            print(f"No {self.category}'s left to map (or none found in current df).")

    def set_ingred_names_to_compare(self):
        """Ingredient names similar to current ingredient."""
        try:
            self.ingred_names_to_compare = difflib.get_close_matches(
                                            self.cur_ingred_name,
                                            self.ingred_names_to_clean.astype('str').unique(),
                                            n=10000,
                                            cutoff=0.6
                                            )
        except AttributeError:
            self.ingred_names_to_compare = []


def load_map(fname):
    """Given a fname (pickle), load in the map."""
    try:
        with open(fname, "rb") as f:
            d = pickle.load(f)
            print(f"Loaded {fname}. Contains {len(d)} keys.")
            return d
    except FileNotFoundError:
        print("No previous map found. Starting from scratch.")
        return {}


def save_map(fname, ingred_map):
    """ Given a fname (pickle), and the current map, save the current map. """
    try:
        with open(fname, "wb") as f:
            pickle.dump(ingred_map, f)
        print(f"Saved {fname}.")
    except NameError:
        print("Trying to save the map, but no map to save. Run map.")


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
    Cleaner().cmdloop()

