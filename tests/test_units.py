"""Identify if columns of data in the recipes are within expected ranges."""

import argparse
import pandas as pd

function_map = {}


def register(s):
    """Register a function into a dict."""

    def inner(f):
        function_map[s] = f
        return f

    return inner


@register("efficiency")
def efficiency(core, ing):
    """Check if efficiency exists and is between 0 and 1"""
    print("Efficiency Sanity")
    n_na = core["efficiency"].isna().sum()
    n_exist = len(core) - n_na
    print(f"----{n_exist} exist, {n_na} NaNs.")
    col = core["efficiency"].dropna()
    n_good = ((col <= 1) & (col > 0)).sum()
    n_bad = ((col > 1) | (col <= 0)).sum()
    print(f"----{n_good} between 0-1, {n_bad} out of range.")


@register("boilbatch")
def boil_batch(core, ing):
    """Check which recipes have sane boil/batch sizes and times."""
    print("Boil/Batch Sanity")
    one_exists = (~core["boil_size"].isna() & ~core["batch_size"].isna()).sum()
    neither_exists = len(core) - one_exists
    print(f"----{one_exists} has at least one, {neither_exists} has neither.")
    bad_values = ((core["boil_size"] <= 0) & (core["batch_size"] <= 0)).sum()
    print(f"----{bad_values} have batch/boil <= 0.")
    boil_gt = (core["boil_size"] > 4).sum()
    boil_lt = len(core) - boil_gt
    batch_gt = (core["batch_size"] > 4).sum()
    batch_lt = len(core) - batch_gt
    print(
        f"----{batch_gt},{boil_gt} batch,boil greater than 4 L, {batch_lt},{boil_lt} less."
    )
    # 1440 = minutes per day
    good_time = ((core["boil_time"] > 0) & (core["boil_time"] < 1440)).sum()
    print(f"----{good_time}/{len(core)} boil times between 0 and 1440 minutes.")


@register("ferm")
def ferm(core, ing):
    """Check ferm amounts, yields, and color."""
    print("Ferm Sanity")
    ferm_cols = [i for i in ing.columns if i.startswith("ferm")]
    gb = ing[ferm_cols].groupby("id")
    non_nan = ~gb[["ferm_amount", "ferm_yield", "ferm_color"]].apply(
        lambda x: x.isnull().all()
    )
    # Amount
    print(f"----{non_nan['ferm_amount'].sum()}/{len(core)} have ferm amounts")
    gt_zero = gb["ferm_amount"].apply(lambda x: (x > 0).all())
    print(f"----{gt_zero.sum()}/{len(core)} have all ferm amounts > 0")
    # Yield
    print(f"----{non_nan['ferm_yield'].sum()}/{len(core)} have ferm yields")
    in_range = gb["ferm_yield"].apply(lambda x: ((x > 0) & (x <= 1)).all())
    print(f"----{in_range.sum()}/{len(core)} have ferm yields in range (0-1)")
    # Color
    print(f"----{non_nan['ferm_color'].sum()}/{len(core)} have ferm colors")
    in_range = gb["ferm_color"].apply(lambda x: ((x > 0) & (x <= 1000)).all())
    print(f"----{in_range.sum()}/{len(core)} have ferm colors in range (0-1000)")


@register("hop")
def hop(core, ing):
    """Check hop amounts, alpha, time, form, and use."""
    print("Hop Sanity")
    hop_cols = [i for i in ing.columns if i.startswith("hop")]
    # Hop amount
    non_nan = ing["hop_amount"].dropna()
    lt_zero = non_nan[non_nan <= 0]
    gt_zero = len(non_nan.index.unique()) - lt_zero.index.nunique()
    print(
        f"----{len(non_nan.index.unique())}/{len(core)} recipes have at least 1 hop. Of those, {gt_zero}/{len(non_nan.index.unique())} are > 0."
    )
    # Hop Alpha


def main(functions=[]):

    if functions == []:
        functions = function_map.keys()
    # test size
    n = 1000

    with pd.HDFStore("../all_recipes.h5", "r") as store:
        core = store.select("core", where=f"index < {n}")
        ing = store.select("ingredients", where=f"index < {n}")

    for func_str in functions:
        function_map[func_str](core, ing)


def make_args():
    parser = argparse.ArgumentParser(
        description="Script to check if different data columns are in expected ranges."
    )
    # Add arguments for each runnable function?
    parser.add_argument(
        "-f",
        "--function",
        help="Function to run.",
        choices=function_map.keys(),
        action="append",
        dest="functions",
    )

    return parser


if __name__ == "__main__":
    parser = make_args()
    args = parser.parse_args()
    if args.functions is None:
        args.functions = function_map.keys()
    main(args.functions)
