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
    cur_ingred_target = None
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

    def help_set_cat(self):
        print(f"Set the category to be mapped. Acceptable values are {VALID_CATEGORIES}.")

    def do_status(self, arg):
        """Print the current status of important variables, maps, etc."""
        if self.category:
            print(f"    Category: {self.category}")
            print(f"    N of ingredients mapped: {len(self.ingred_map.keys())}")
            print(f"    Current ingredient to map: {self.cur_ingred_target}")
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
            unique = self.ingred_names_to_clean.value_counts()
            print(f"    {len(unique)} unique ingredient names left to clean.")
            print(f"Next 3 to clean (name, count):")
            print(f"{unique.head(3)}")

    def help_remain(self, arg):
        print("Print the remaining ingreds_names_similar or ingreds_to_map")
        
    def do_impact(self, arg):
        """Print the number of times the current ingredient appears in the ingredients to clean.
        This is the number of records affected by the current mapping decision."""
        num_records_affected = self.ingred_names_to_clean.value_counts()[self.cur_ingred_compare]
        print(f"Records affected by mapping {self.cur_ingred_compare}: {num_records_affected}")
        
    def help_impact(self, arg):
        print("Print the number of times the current ingredient appears in the ingredients to clean. \
        This is the number of records affected by the current mapping decision.")

    def do_map(self, arg):
        """Begin the process of finding similar strings to the top unmapped ingredient."""
        # If there's no category set, give a warning and pass
        if self.category is None:
            print("No category set. Run set_cat.")
            return
        
        self.active = True
        # If we haven't mapped before this session, start by advancing the ingredient (which will update the prompt)
        if self.cur_ingred_target is None:
            self.advance_ingred()
        # If we've already started mapping, don't update the ingredient. Just update the prompt
        else: 
            self.set_prompt_compare()

    def help_map(self):
        print("Begin the process of finding similar strings to the top unmapped ingredient.")

    def do_y(self, arg):
        """Approve cur_ingred_compare to map to cur_ingred_target and advance
        to the next target ingredient."""
        print("Accepted.")
        self.ingred_map[self.cur_ingred_compare] = self.cur_ingred_target
        save_map(self.map_name, self.ingred_map)
        self.advance_ingred()

    def do_n(self, arg):
        """Reject cur_ingred_compare to map to cur_ingred_target. Advance to the
        next ingredient."""
        print("Rejected.")
        self.advance_ingred()

    def do_rename(self, arg):
        """Rename the [current | specific] target ingredient."""
        if arg == "":
            print("Pass string to rename to.")
            return
        for k, v in self.ingred_map.items():
            if v == self.cur_ingred_target:
                self.ingred_map[k] = arg
        self.cur_ingred_target = arg
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
            print(f"Excluding ingredients containing {s}: {exclude_ingred}")
            # Exclude them 
            self.ingred_names_to_compare = [i for i in self.ingred_names_to_compare if s not in i]
            # If the string to exclude is in the current one, reject it and advance the ingredient 
            if s in self.cur_ingred_compare:
                print(f"Current ingredient rejected as part of excluding {s}.")
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
        available) and update the prompt."""
        try:
            tmp = self.cur_ingred_compare
            self.cur_ingred_compare = self.ingred_names_to_compare.pop(0)
            self.prev_ingreds_compare.append(tmp)   
            self.set_prompt_compare()
        # In two scenarios, advance the target instead of the ingredient: 
        #   When we're done mapping a target
        #   Or if there's no target set (we haven't started mapping yet)
        except IndexError:
            # Advance the ingredient to map
            self.advance_ingred_target()
    
    def advance_ingred_target(self):  
        """Get a new target, list of names to compare to it, and next name to compare.
        Update the prompt."""
        
        self.set_cur_ingred_target()
        print(f"Starting mapping for {self.cur_ingred_target}.")
        # Add the trivial mapping 
        self.ingred_map[self.cur_ingred_target] = self.cur_ingred_target
        
        self.set_ingred_names_to_compare()
        self.cur_ingred_compare = self.ingred_names_to_compare.pop(0)
        self.set_prompt_compare()
    
    def set_prompt_compare(self):
        """Set the prompt according to the current ingred_name and
        ingred_compare"""
        self.prompt = self.cur_ingred_target + " == " + self.cur_ingred_compare
        self.prompt += PROMPT_SUFFIX

    def set_cur_ingred_target(self):
        """Get the next target: the next ingredient to map to."""
        # Get the most common unique name remaining
        try:
            # self.cur_ingred_target = self.ingred_names_to_clean.value_counts().index[self.index]
            self.cur_ingred_target = self.ingred_names_to_clean.value_counts().index[0]
        except IndexError:
            print(f"No {self.category}'s left to map (or none found in current df).")

    def set_ingred_names_to_compare(self):
        """Ingredient names similar to current ingredient."""
        try:
            self.ingred_names_to_compare = difflib.get_close_matches(
                                            self.cur_ingred_target,
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

