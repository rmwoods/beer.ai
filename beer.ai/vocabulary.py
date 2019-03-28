import argparse
import pandas
import pickle

VALID_CATS = ["ferm", "yeast", "hop", "misc"]
MAP_NAME = "{}map.pickle"


def create_vocab(category, out_file=None):
    """Given a category, load in the corresponding columns from the HDF and
    create unique id's for each ingredient. Valid categories:
        [ferm, yeast, hop, misc]

    Note: We can make the assumption that the set of unique values we want are
    the values from the _map.pickle files.
    """
    if out_file == None:
        out_file = category + "_vocab.pickle"

    map_name = MAP_NAME.format(category)
    with open(map_name, "rb") as f:
        ing_map = pickle.load(f)
    
    ings = sorted(set(ing_map.values()))
    vocab = {ing:i for i,ing in enumerate(ings)}
    with open(out_file, "wb") as f:
        pickle.dump(vocab, f)


def _setup_argparser():
    parser = argparse.ArgumentParser(
        description="Program to create a \"vocabulatory\" from a list of "
            "ingredients (unique index per ingredient)."
    )
    parser.add_argument(
        "-c",
        "--category",
        required=True,
        choices=VALID_CATS,
        help="Category to create vocab for."
    )
    parser.add_argument(
        "-o",
        "--output_file",
        help="File to dump vocabulary to."
    )
    return parser


if __name__=="__main__":
    parser = _setup_argparser()
    args = parser.parse_args()
    create_vocab(args.category, args.output_file)
