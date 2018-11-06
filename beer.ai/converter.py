"""Script to convert beer XMLs to a ML friendly format."""

import argparse
import glob
import os.path as path
import numpy as np
import pandas as pd
import random
import re
import warnings

from joblib import delayed, Parallel
from pybeerxml import Parser

# From https://coderwall.com/p/xww5mq/two-letter-country-code-regex
ORIGIN_RE = "\((AF|AX|AL|DZ|AS|AD|AO|AI|AQ|AG|AR|AM|AW|AU|AT|AZ|BS|BH|BD|BB|BY|BE|BZ|BJ|BM|BT|BO|BQ|BA|BW|BV|BR|IO|BN|BG|BF|BI|KH|CM|CA|CV|KY|CF|TD|CL|CN|CX|CC|CO|KM|CG|CD|CK|CR|CI|HR|CU|CW|CY|CZ|DK|DJ|DM|DO|EC|EG|SV|GQ|ER|EE|ET|FK|FO|FJ|FI|FR|GF|PF|TF|GA|GM|GE|DE|GH|GI|GR|GL|GD|GP|GU|GT|GG|GN|GW|GY|HT|HM|VA|HN|HK|HU|IS|IN|ID|IR|IQ|IE|IM|IL|IT|JM|JP|JE|JO|KZ|KE|KI|KP|KR|KW|KG|LA|LV|LB|LS|LR|LY|LI|LT|LU|MO|MK|MG|MW|MY|MV|ML|MT|MH|MQ|MR|MU|YT|MX|FM|MD|MC|MN|ME|MS|MA|MZ|MM|NA|NR|NP|NL|NC|NZ|NI|NE|NG|NU|NF|MP|NO|OM|PK|PW|PS|PA|PG|PY|PE|PH|PN|PL|PT|PR|QA|RE|RO|RU|RW|BL|SH|KN|LC|MF|PM|VC|WS|SM|ST|SA|SN|RS|SC|SL|SG|SX|SK|SI|SB|SO|ZA|GS|SS|ES|LK|SD|SR|SJ|SZ|SE|CH|SY|TW|TJ|TZ|TH|TL|TG|TK|TO|TT|TN|TR|TM|TC|TV|UG|UA|AE|GB|UK|US|UM|UY|UZ|VU|VE|VN|VG|VI|WF|EH|YE|ZM|ZW)\)"
MODIFIER_RE = "\(\w*\)"
LEAF_STR = "leaf"
N_CPUS = -1


def clean_text(text):
    """Standard method for cleaning text in our recipes. Any changes to parsing
    and storing text fields should happen here."""
    if text is not None:
        return str(text).lower().strip()


def remove_ingredient_modifiers(text):
    """Given an ingredient string, remove any modifiers, e.g. 'Cinnamon (Ground)'
    would return 'Cinnamon '."""
    mod_text = text
    if mod_text is not None:
        m = re.search(MODIFIER_RE, mod_text)
        if m is not None:
            span = m.span()
            mod_text = mod_text[:span[0]] + mod_text[span[1]:]
    return mod_text


def check_origin(text):
    """Check a text object to see if 'origin' was included in it in the form of
    '(US)'. If so, return the original text object with that bit stripped, and
    the origin. Otherwise, return the original string and None."""
    origin = None
    mod_text = text
    if mod_text is not None:
        m = re.search(ORIGIN_RE, text)
        if m is not None:
            span = m.span()
            # strip parens
            origin = m.group()[1:-1]
            mod_text = mod_text[:span[0]] + mod_text[span[1]:]
    return mod_text, origin


def safe_float(arg):
    """Try to convert to float, return None otherwise."""
    if arg is not None:
        return float(arg)


def recipe_to_df(recipe, fname):
    """Given a pybeerxml.recipe.Recipe, convert to a dataframe and write in a
    more efficient format.
    """

    to_df = {}
    to_df["recipe_file"] = fname
    to_df["name"] = clean_text(recipe.name)
    to_df["batch_size"] = safe_float(recipe.batch_size)
    if to_df["batch_size"] == 0:
        to_df["batch_size"] = 1
    to_df["boil_size"] = safe_float(recipe.boil_size)
    if to_df["boil_size"] == 0:
        to_df["boil_size"] = 1
    to_df["efficiency"] = safe_float(recipe.efficiency)/100.

    for i, ferm in enumerate(recipe.fermentables):
        col = f"ferm{i}_"
        yeast_name, yeast_origin = check_origin(ferm.name)
        to_df[col + "name"] = clean_text(yeast_name)
        if yeast_origin is not None:
            to_df[col + "origin"] = clean_text(yeast_origin)
        else:
            to_df[col + "origin"] = clean_text(ferm.origin)
        to_df[col + "amount"] = safe_float(ferm.amount)
        to_df[col + "display_amount"] = clean_text(ferm.display_amount)
        to_df[col + "yield"] = safe_float(ferm._yield)*0.01
        # malt_scaled = <amount> * <yield> * <efficiency> / <boil_size>
        to_df[col + "scaled"] = to_df[col + "amount"] * to_df[col + "yield"]\
                                * to_df["efficiency"] / to_df["boil_size"]

    for i, hop in enumerate(recipe.hops):
        col = f"hop{i}_"
        hop_name, hop_origin = check_origin(hop.name)
        to_df[col + "name"] = clean_text(hop_name)
        if hop_origin is not None:
            to_df[col + "origin"] = clean_text(hop_origin)
        else:
            to_df[col + "origin"] = clean_text(hop.origin)
        to_df[col + "amount"] = safe_float(hop.amount)
        to_df[col + "display_amount"] = clean_text(hop.display_amount)
        to_df[col + "alpha"] = safe_float(hop.alpha)/100.
        to_df[col + "form"] = clean_text(hop.form)
        is_leaf = int(to_df[col + "form"] == LEAF_STR)
        to_df[col + "time"] = safe_float(hop.time)
        if to_df[col + "time"] > 0:
            # hop_scaled  = <amount>*0.01*<alpha>*[1 - 0.1 * (leaf)]/<boil_size>
            to_df[col + "scaled"] = (to_df[col + "amount"]
                                    * to_df[col + "alpha"] * (1 - 0.1 * is_leaf))\
                                    / to_df["boil_size"]
        else:
            # dry_hop_scaled = <amount> / <batch_size>
            to_df[col + "scaled"] = to_df[col + "amount"] / to_df["batch_size"]

    for i, yeast in enumerate(recipe.yeasts):
        col = f"yeast{i}_"
        to_df[col + "name"] = clean_text(yeast.name)
        to_df[col + "laboratory"] = clean_text(yeast.laboratory)
        
    for i, misc in enumerate(recipe.miscs):
        col = f"miscs{i}_"
        misc_name = remove_ingredient_modifiers(misc.name)
        to_df[col + "name"] = clean_text(misc_name)
        to_df[col + "amount"] = safe_float(misc.amount)
        to_df[col + "use"] = clean_text(misc.use)
        to_df[col + "time"] = safe_float(misc.time)

    df = pd.DataFrame(data=to_df, index=[0])
    return df


def convert_runner(fname):
    """Meant to be run on a single recipe file."""
    parser = Parser()
    recipes = parser.parse(fname)
    try:
        recipe = recipes[0]
    except IndexError:
        print(f"No recipe in {fname}")
        return None
    try:
        df = recipe_to_df(recipe, fname)
    except Exception as e:
        print(f"Failed {fname}:")
        print(e)
        df = pd.DataFrame()
    return df


def convert_a_bunch(path_to_recipes, n):
    """Convert n randomly chosen recipes. Currently for inspecting the output."""

    if path_to_recipes is not None:
        samples = path_to_recipes
    else:
        recipe_files = glob.glob(path.join("recipes", "*.xml"))
        if n != -1:
            samples = random.sample(recipe_files, n)
        else:
            samples = recipe_files

    results = Parallel(n_jobs=N_CPUS)(delayed(convert_runner)(fname) for fname in samples)

    dfs = []
    for result in results:
        dfs.append(result)
    df = pd.concat(dfs, axis=0, sort=False)

    # Calculate a filename as a hash of the xml files that were read in.
    fname = str(abs(hash(tuple(samples)))) + ".h5"
    print(f"Writing results to {fname}")
    #with warnings.catch_warnings():
        #warnings.simplefilter("ignore", category=PerformanceWarning)
    df.to_hdf(fname, "test", complevel=9, complib="blosc")


def _setup_argparser():
    parser = argparse.ArgumentParser(
        description="Program to convert a specific list or a random list of "
            "recipes to an hdf for inspection."
    )
    parser.add_argument(
        "-f",
        "--filename",
        action="append",
        help="Specific recipe filename to parse. Can pass argument multiple "
            "times to specify multiple recipes to convert."
    )
    parser.add_argument(
        "-n",
        "--number",
        type=int,
        default=20,
        help="If randomly parsing, number of recipes to randomly select for "
            "conversion. Note that -1 means to convert *all* recipes. Default "
            "is 20."
    )
    return parser


if __name__=="__main__":
    parser = _setup_argparser()
    args = parser.parse_args()

    convert_a_bunch(args.filename, args.number)
