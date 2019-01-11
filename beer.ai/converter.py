"""Script to convert beer XMLs to a ML friendly format."""

import argparse
import glob
import os.path as path
import numpy as np
import pandas as pd
import random
import re

from itertools import zip_longest
from joblib import delayed, Parallel
from pybeerxml import Parser

# From https://coderwall.com/p/xww5mq/two-letter-country-code-regex
ORIGIN_RE = re.compile("\((AF|AX|AL|DZ|AS|AD|AO|AI|AQ|AG|AR|AM|AW|AU|AT|AZ|BS|BH|BD|BB|BY|BE|BZ|BJ|BM|BT|BO|BQ|BA|BW|BV|BR|IO|BN|BG|BF|BI|KH|CM|CA|CV|KY|CF|TD|CL|CN|CX|CC|CO|KM|CG|CD|CK|CR|CI|HR|CU|CW|CY|CZ|DK|DJ|DM|DO|EC|EG|SV|GQ|ER|EE|ET|FK|FO|FJ|FI|FR|GF|PF|TF|GA|GM|GE|DE|GH|GI|GR|GL|GD|GP|GU|GT|GG|GN|GW|GY|HT|HM|VA|HN|HK|HU|IS|IN|ID|IR|IQ|IE|IM|IL|IT|JM|JP|JE|JO|KZ|KE|KI|KP|KR|KW|KG|LA|LV|LB|LS|LR|LY|LI|LT|LU|MO|MK|MG|MW|MY|MV|ML|MT|MH|MQ|MR|MU|YT|MX|FM|MD|MC|MN|ME|MS|MA|MZ|MM|NA|NR|NP|NL|NC|NZ|NI|NE|NG|NU|NF|MP|NO|OM|PK|PW|PS|PA|PG|PY|PE|PH|PN|PL|PT|PR|QA|RE|RO|RU|RW|BL|SH|KN|LC|MF|PM|VC|WS|SM|ST|SA|SN|RS|SC|SL|SG|SX|SK|SI|SB|SO|ZA|GS|SS|ES|LK|SD|SR|SJ|SZ|SE|CH|SY|TW|TJ|TZ|TH|TL|TG|TK|TO|TT|TN|TR|TM|TC|TV|UG|UA|AE|GB|UK|US|UM|UY|UZ|VU|VE|VN|VG|VI|WF|EH|YE|ZM|ZW)\)")
RECIPES_DIR = "test_recipes"
MODIFIER_RE = re.compile("\([\w ]*\)")
LEAF_STR = "leaf"

# Number of processors to use. -1 = all
N_CPUS = -1


def clean_text(text):
    """Standard method for cleaning text in our recipes. Any changes to parsing
    and storing text fields should happen here."""
    if text is not None:
        return str(text).lower().strip()


def remove_ingredient_modifiers(text):
    """Given an ingredient string, remove any modifiers, e.g. 'Cinnamon (Ground)'
    would return 'Cinnamon '."""
    mod_text = str(text)
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
    mod_text = str(text)
    if mod_text is not None:
        m = re.search(ORIGIN_RE, mod_text)
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
    else:
        return np.nan


def add_to_dicts(to_df, key, value, dtype_dict):
    """set to_df[key] = value, infer type of value, and set type[key] = type."""
    to_df[key] = value
    if isinstance(value, str):
        dtype_dict[key] = "string"
    else:
        dtype_dict[key] = "float32"


def fill_ferm(d, ferm, core_vals):
    """Given a ferm class, add the appropriate fields to the dict d."""
    if ferm is not None:
        ferm_name, ferm_origin = check_origin(ferm.name)
        d["ferm_name"] = clean_text(ferm_name)
        if ferm_origin is not None:
            d["ferm_origin"] = clean_text(ferm_origin)
        else:
            d["ferm_origin"] = clean_text(ferm.origin)
        d["ferm_amount"] = safe_float(ferm.amount)
        d["ferm_display_amount"] = clean_text(getattr(ferm, "display_amount", ""))
        d["ferm_yield"] = safe_float(ferm._yield)*0.01
        # malt_scaled = <amount> * <yield> * <efficiency> / <boil_size>
        d["ferm_scaled"] = d["ferm_amount"] * d["ferm_yield"]\
                                * core_vals["efficiency"] / core_vals["boil_size"]


def fill_hop(d, hop, core_vals):
    """Given a hop class, add the appropriate fields to the dict d."""
    if hop is not None:
        hop_name, hop_origin = check_origin(hop.name)
        d["hop_name"] = clean_text(hop_name)
        if hop_origin is not None:
            d["hop_origin"] = clean_text(hop_origin)
        else:
            d["hop_origin"] = clean_text(getattr(hop, "origin",""))
        d["hop_amount"] = safe_float(hop.amount)
        d["hop_display_amount"] = clean_text(getattr(hop, "display_amount", ""))
        d["hop_alpha"] = safe_float(hop.alpha)/100.
        d["hop_form"] = clean_text(hop.form)
        is_leaf = int(d["hop_form"] == LEAF_STR)
        d["hop_time"] = safe_float(hop.time)
        if d["hop_time"] > 0:
            # hop_scaled  = <amount>*0.01*<alpha>*[1 - 0.1 * (leaf)]/<boil_size>
            d["hop_scaled"] = (d["hop_amount"]
                               * d["hop_alpha"] * (1 - 0.1 * is_leaf))\
                               / core_vals["boil_size"]
        else:
            # dry_hop_scaled = <amount> / <batch_size>
            d["hop_scaled"] = d["hop_amount"] / core_vals["batch_size"]


def fill_yeast(d, yeast):
    """Given a yeast class, add the appropriate fields to the dict d."""
    if yeast is not None:
        d["yeast_name"] = clean_text(yeast.name)
        d["yeast_laboratory"] = clean_text(yeast.laboratory)


def fill_misc(d, misc):
    """Given a misc class, add the appropriate fields to the dict d."""
    if misc is not None:
        misc_name = remove_ingredient_modifiers(misc.name)
        d["misc_name"] = clean_text(misc_name)
        d["misc_amount"] = safe_float(misc.amount)
        d["misc_use"] = clean_text(misc.use)
        d["misc_time"] = safe_float(misc.time)
        # Should be a boolean
        d["misc_amount_is_weight"] = misc.amount_is_weight or False


def fill_core(d, recipe):
    """Given a dictionary, put all the core value items from the recipe object
    into the dict."""

    d["name"] = clean_text(recipe.name)

    d["batch_size"] = safe_float(recipe.batch_size)
    if d["batch_size"] == 0:
        d["batch_size"] = 1
    d["boil_size"] = safe_float(recipe.boil_size)
    if d["boil_size"] == 0:
        d["boil_size"] = 1
    d["efficiency"] = safe_float(recipe.efficiency)/100.
    d["boil_time"] = safe_float(recipe.boil_time)

    d["style_name"] = clean_text(recipe.style.name)
    d["style_guide"] = clean_text(recipe.style.style_guide)
    d["style_category"] = str(int(safe_float(recipe.style.category_number))) + clean_text(recipe.style.style_letter)
    d["style_version"] = safe_float(recipe.style.version)


def recipe_to_dicts(recipe, fname, recipe_id):
    """Given a pybeerxml.recipe.Recipe, convert to a dataframe and write in a
    more efficient format.
    """

    core_vals = {}
    ingredients = []
    core_vals["id"] = recipe_id
    core_vals["recipe_file"] = fname
    fill_core(core_vals, recipe)

    for ferm, hop, yeast, misc in zip_longest(
            recipe.fermentables, recipe.hops, recipe.yeasts, recipe.miscs):
        tmp = {"id": recipe_id}
        fill_ferm(tmp, ferm, core_vals)
        fill_hop(tmp, hop, core_vals)
        fill_yeast(tmp, yeast)
        fill_misc(tmp, misc)
        ingredients.append(tmp)

    return core_vals, ingredients


def convert_runner(fname, recipe_id):
    """Meant to be run on a single recipe file."""
    parser = Parser()
    print(fname)
    recipes = parser.parse(fname)
    try:
        recipe = recipes[0]
    except IndexError:
        print(f"No recipe in {fname}")
        return None
    try:
        core_vals, ingredients = recipe_to_dicts(recipe, fname, recipe_id)
    except Exception as e:
        print(f"Failed {fname}:")
        print(e)
        core_vals, ingredients = {}, []
    return core_vals, ingredients


def clean_cols(df):
    """For certain columns, fill in values to make writing succeed."""
    if "misc_amount_is_weight" in df.columns:
        df["misc_amount_is_weight"] = df["misc_amount_is_weight"].fillna(False)


def convert_a_bunch(path_to_recipes, n, jobs=N_CPUS):
    """Convert n randomly chosen recipes. Currently for inspecting the output."""

    if path_to_recipes is not None:
        samples = path_to_recipes
    else:
        recipe_files = glob.glob(path.join(RECIPES_DIR, "*.xml"))
        if n != -1:
            # Make sure we don't try to grab more than exist
            n = min(n, len(recipe_files))
            samples = random.sample(recipe_files, n)
        else:
            samples = recipe_files

    results = Parallel(n_jobs=jobs)(
            delayed(convert_runner)(fname, i)
            for i, fname in enumerate(samples))

    core_vals = []
    ingredients = []
    for result in results:
        core_vals.append(result[0])
        ingredients.extend(result[1])
    
    df_core = pd.DataFrame(core_vals)
    df_core = df_core.set_index("id")
    
    df_ing = pd.DataFrame(ingredients)
    df_ing = df_ing.set_index("id")
    clean_cols(df_ing)

    write_options = {
        "complevel": 9,
        "complib": "blosc",
        "format": "table",
    }
    if n == -1:
        fname = "all_recipes.h5"
    else:
        # Calculate a filename as a hash of the xml files that were read in.
        fname = str(abs(hash(tuple(samples)))) + ".h5"
    print(f"Writing {len(samples)} examples to {fname}.")
    df_core.to_hdf(fname, "core", mode="w", **write_options)
    df_ing.to_hdf(fname, "ingredients", mode="a", **write_options)


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
    parser.add_argument(
        "-j",
        "--jobs",
        type=int,
        default=N_CPUS,
        help="Number of processors to use."
    )
    return parser


if __name__ == "__main__":
    parser = _setup_argparser()
    args = parser.parse_args()

    convert_a_bunch(args.filename, args.number, args.jobs)
