import argparse
import os
import pickle

from ..config import DATA_DIR, INGREDIENT_CATEGORIES

MAP_NAME = os.path.join(DATA_DIR, "interim/{}map.pickle")


def create_vocab(out_file=None):
    """Given a category, load in the corresponding columns from the HDF and
    create unique id's for each ingredient. Valid categories:
        [ferm, yeast, hop, misc]

    Note: We can make the assumption that the set of unique values we want are
    the values from the _map.pickle files.
    """
    if out_file is None:
        out_file = os.path.join(DATA_DIR, "processed/vocab.pickle")

    vocab = {}
    for category in INGREDIENT_CATEGORIES:
        map_name = MAP_NAME.format(category)
        with open(map_name, "rb") as f:
            ing_map = pickle.load(f)
            ings = sorted(set(ing_map.values()))
            vocab.update(
                {category + "_" + ing: i for i, ing in enumerate(ings, len(vocab))}
            )
            if category == "hop":
                vocab.update(
                    {
                        category + "_" + ing + "_dry": i
                        for i, ing in enumerate(ings, len(vocab))
                    }
                )

    with open(out_file, "wb") as f:
        pickle.dump(vocab, f)


def _setup_argparser():
    parser = argparse.ArgumentParser(
        description='Program to create a "vocabulatory" from a list of '
        "ingredients (unique index per ingredient)."
    )
    parser.add_argument(
        "-o",
        "--output_file",
        help="File to dump vocabulary to. Default is `data/processed/vocab.pickle`.",
    )
    return parser


if __name__ == "__main__":
    parser = _setup_argparser()
    args = parser.parse_args()
    create_vocab(args.output_file)
