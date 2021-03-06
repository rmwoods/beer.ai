"""Script to convert beer XMLs to a ML friendly format."""

import argparse
import os
import numpy as np
import pandas as pd
import random
import re
import sys

from itertools import zip_longest
from joblib import delayed, Parallel
from pybeerxml import Parser
from xml.etree.ElementTree import ParseError

from ..config import DATA_DIR

# From https://coderwall.com/p/xww5mq/two-letter-country-code-regex
ORIGIN_RE = re.compile(
    "\((AF|AX|AL|DZ|AS|AD|AO|AI|AQ|AG|AR|AM|AW|AU|AT|AZ|BS|BH|BD|BB|BY|BE|BZ|BJ|BM|BT|BO|BQ|BA|BW|BV|BR|IO|BN|BG|BF|BI|KH|CM|CA|CV|KY|CF|TD|CL|CN|CX|CC|CO|KM|CG|CD|CK|CR|CI|HR|CU|CW|CY|CZ|DK|DJ|DM|DO|EC|EG|SV|GQ|ER|EE|ET|FK|FO|FJ|FI|FR|GF|PF|TF|GA|GM|GE|DE|GH|GI|GR|GL|GD|GP|GU|GT|GG|GN|GW|GY|HT|HM|VA|HN|HK|HU|IS|IN|ID|IR|IQ|IE|IM|IL|IT|JM|JP|JE|JO|KZ|KE|KI|KP|KR|KW|KG|LA|LV|LB|LS|LR|LY|LI|LT|LU|MO|MK|MG|MW|MY|MV|ML|MT|MH|MQ|MR|MU|YT|MX|FM|MD|MC|MN|ME|MS|MA|MZ|MM|NA|NR|NP|NL|NC|NZ|NI|NE|NG|NU|NF|MP|NO|OM|PK|PW|PS|PA|PG|PY|PE|PH|PN|PL|PT|PR|QA|RE|RO|RU|RW|BL|SH|KN|LC|MF|PM|VC|WS|SM|ST|SA|SN|RS|SC|SL|SG|SX|SK|SI|SB|SO|ZA|GS|SS|ES|LK|SD|SR|SJ|SZ|SE|CH|SY|TW|TJ|TZ|TH|TL|TG|TK|TO|TT|TN|TR|TM|TC|TV|UG|UA|AE|GB|UK|US|UM|UY|UZ|VU|VE|VN|VG|VI|WF|EH|YE|ZM|ZW)\)"
)
MODIFIER_RE = re.compile("\([\w ]*\)")

UNIT_RE = re.compile("(?P<amount>\d*\.?\d*) *(?P<unit>g|kg|oz|lb)")
TO_KG = {"kg": 1, "g": 0.001, "oz": 0.0283495, "lb": 0.453592}
EPS = 1e-7

# Number of processors to use. -1 = all
N_CPUS = -1

CLEAN_STEPS = {
    "style_category": {"type": str},
    "misc_amount_is_weight": {"type": bool, "fill": False},
    "yeast_product_id": {"type": str, "fill": np.nan},
}


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
            mod_text = mod_text[: span[0]] + mod_text[span[1] :]
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
            mod_text = mod_text[: span[0]] + mod_text[span[1] :]
    return mod_text, origin


def safe_float(arg):
    """Try to convert to float, return None otherwise."""
    if arg is not None:
        return float(arg)
    else:
        return np.nan


def extract_amount_unit(text):
    if text is not None:
        m = re.search(UNIT_RE, text)
        if m is not None:
            return float(m.group("amount")), m.group("unit").lower()
    return None, None


def fill_ferm(d, ferm, core_vals):
    """Given a ferm class, add the appropriate fields to the dict d."""
    if ferm is not None:
        ferm_name, ferm_origin = check_origin(getattr(ferm, "name", None))
        d["ferm_name"] = clean_text(ferm_name)
        if ferm_origin is not None:
            d["ferm_origin"] = clean_text(ferm_origin)
        else:
            d["ferm_origin"] = clean_text(getattr(ferm, "origin", None))
        d["ferm_amount"] = safe_float(getattr(ferm, "amount", None))
        d["ferm_display_amount"] = clean_text(getattr(ferm, "display_amount", None))
        amount, unit = extract_amount_unit(getattr(ferm, "display_amount", None))
        if (
            amount is not None
            and unit is not None
            and d["ferm_amount"] is not None
            and abs(amount * TO_KG.get(unit, 1) - d["ferm_amount"]) > EPS
        ):
            d["ferm_amount"] = amount * TO_KG.get(unit, 1)
        d["ferm_yield"] = safe_float(getattr(ferm, "_yield", None)) * 0.01
        d["ferm_color"] = safe_float(getattr(ferm, "color", None))
        d["ferm_potential"] = safe_float(getattr(ferm, "potential", None))


def fill_hop(d, hop, core_vals):
    """Given a hop class, add the appropriate fields to the dict d."""
    if hop is not None:
        hop_name, hop_origin = check_origin(getattr(hop, "name", None))
        d["hop_name"] = clean_text(hop_name)
        if hop_origin is not None:
            d["hop_origin"] = clean_text(hop_origin)
        else:
            d["hop_origin"] = clean_text(getattr(hop, "origin", None))
        d["hop_amount"] = safe_float(getattr(hop, "amount", None))
        d["hop_display_amount"] = clean_text(getattr(hop, "display_amount", None))
        amount, unit = extract_amount_unit(getattr(hop, "display_amount", None))
        if (
            amount is not None
            and unit is not None
            and d["hop_amount"] is not None
            and abs(amount * TO_KG.get(unit, 1) - d["hop_amount"]) > EPS
        ):
            d["hop_amount"] = amount * TO_KG.get(unit, 1)
        d["hop_alpha"] = safe_float(getattr(hop, "alpha", None))
        if d["hop_alpha"] is not None:
            d["hop_alpha"] /= 100.0
        d["hop_form"] = clean_text(getattr(hop, "form", None))
        # From brewerstoad:
        # ['boil', 'dry hop', 'first wort', 'whirlpool', 'mash', 'aroma']
        d["hop_use"] = clean_text(getattr(hop, "use", None))
        d["hop_time"] = safe_float(getattr(hop, "time", None))


def fill_yeast(d, yeast):
    """Given a yeast class, add the appropriate fields to the dict d."""
    if yeast is not None:
        yeast_name = str(getattr(yeast, "name", None))
        if yeast_name is not None:
            yeast_name.replace(" yeast", "")
        d["yeast_name"] = clean_text(yeast_name)
        d["yeast_laboratory"] = clean_text(getattr(yeast, "laboratory", None))
        d["yeast_type"] = clean_text(getattr(yeast, "type", None))
        d["yeast_form"] = clean_text(getattr(yeast, "form", None))
        d["yeast_amount"] = safe_float(getattr(yeast, "amount", None))
        d["yeast_product_id"] = getattr(yeast, "product_id", None)
        d["yeast_attenuation"] = safe_float(getattr(yeast, "attenuation", None))
        d["yeast_flocculation"] = clean_text(getattr(yeast, "flocculation", None))


def fill_misc(d, misc):
    """Given a misc class, add the appropriate fields to the dict d."""
    if misc is not None:
        misc_name = remove_ingredient_modifiers(getattr(misc, "name", None))
        d["misc_name"] = clean_text(misc_name)
        d["misc_amount"] = safe_float(getattr(misc, "amount", None))
        d["misc_use"] = clean_text(getattr(misc, "use", None))
        d["misc_time"] = safe_float(getattr(misc, "time", None))
        # Should be a boolean
        d["misc_amount_is_weight"] = getattr(misc, "amount_is_weight", None) or False


def fill_core(d, recipe):
    """Given a dictionary, put all the core value items from the recipe object
    into the dict."""

    if recipe is not None:
        d["name"] = clean_text(getattr(recipe, "name", None))
        d["brewer"] = clean_text(getattr(recipe, "brewer", None))

        d["batch_size"] = safe_float(getattr(recipe, "batch_size", None))
        if d["batch_size"] == 0:
            d["batch_size"] = 1
        d["boil_size"] = safe_float(getattr(recipe, "boil_size", None))
        if d["boil_size"] == 0:
            d["boil_size"] = 1
        d["efficiency"] = safe_float(getattr(recipe, "efficiency", None))
        if d["efficiency"] is not None:
            d["efficiency"] /= 100.0
        d["boil_time"] = safe_float(getattr(recipe, "boil_time", None))

        # beer properties as per recipe source (e.g. brewer's friend)
        d["src_ibu"] = safe_float(getattr(recipe, "ibu", None))
        d["src_og"] = safe_float(getattr(recipe, "og", None))
        d["src_fg"] = safe_float(getattr(recipe, "fg", None))
        d["src_abv"] = safe_float(getattr(recipe, "est_abv", None))
        d["src_color"] = safe_float(getattr(recipe, "est_color", None))

        d["style_name"] = clean_text(getattr(recipe.style, "name", None))
        d["style_guide"] = clean_text(getattr(recipe.style, "style_guide", None))
        d["style_category"] = str(
            int(safe_float(getattr(recipe.style, "category_number", None)))
        ) + clean_text(getattr(recipe.style, "style_letter", None))
        d["style_version"] = safe_float(getattr(recipe.style, "version", None))


def recipe_to_dicts(recipe, fname, recipe_id, origin):
    """Given a pybeerxml.recipe.Recipe, convert to a dataframe and write in a
    more efficient format.
        recipe: pybeerxml Recipe object
        fname: file name that beer xml object came from (for recording)
        recipe_id: unique id to assign to recipe
        origin: source where recipe came from (e.g. brewtoad.com)
    """

    core_vals = {}
    ingredients = []
    core_vals["id"] = recipe_id
    core_vals["recipe_file"] = fname
    core_vals["origin"] = origin
    fill_core(core_vals, recipe)

    for ferm, hop, yeast, misc in zip_longest(
        recipe.fermentables, recipe.hops, recipe.yeasts, recipe.miscs
    ):
        tmp = {"id": recipe_id}
        fill_ferm(tmp, ferm, core_vals)
        fill_hop(tmp, hop, core_vals)
        fill_yeast(tmp, yeast)
        fill_misc(tmp, misc)
        ingredients.append(tmp)

    return core_vals, ingredients


def convert_runner(fname, origin, recipe_id):
    """Meant to be run on a single recipe file."""
    try:
        parser = Parser()
        recipes = parser.parse(fname)
    except ParseError as e:
        print(f"Failed to parse {fname}:", file=sys.stderr)
        print(e, file=sys.stderr)
        return None
    try:
        recipe = recipes[0]
    except IndexError:
        print(f"No recipe in {fname}", file=sys.stderr)
        return None
    try:
        core_vals, ingredients = recipe_to_dicts(recipe, fname, recipe_id, origin)
    except Exception as e:
        print(f"Failed {fname}:", file=sys.stderr)
        print(e, file=sys.stderr)
        core_vals, ingredients = {}, []
    return (core_vals, ingredients)


def clean_cols(df):
    """For any special case columns, clean the column to make sure NaNs and
    dtypes are consistent from chunk to chunk.
    """
    for col in df.columns:
        if col in CLEAN_STEPS.keys():
            steps = CLEAN_STEPS[col]
            step_keys = steps.keys()
            if "fill" in step_keys:
                df[col] = df[col].fillna(value=steps["fill"])
            if "type" in step_keys:
                df[col] = df[col].astype(steps["type"])


def convert_a_bunch(filenames, n, jobs=N_CPUS):
    """Convert n randomly chosen recipes. Currently for inspecting the output."""

    if filenames is not None:
        samples = [(f.split("/")[-2], f) for f in filenames]
    else:
        # Note that this is a bit slower than just assuming the source directory
        # has a certain structure of origin/*.xml and letting the OS glob the files
        recipe_files = []
        recipes_dir = os.path.join(DATA_DIR, "raw/recipes")
        for dirpath, dirnames, filenames in os.walk(recipes_dir):
            for f in filenames:
                if f.endswith("xml"):
                    origin = dirpath.split("/")[-1]
                    fpath = os.path.join(dirpath, f)
                    recipe_files.append((origin, fpath))
        if n != -1:
            samples = random.sample(recipe_files, min(len(recipe_files), n))
        else:
            samples = recipe_files

    results = Parallel(n_jobs=jobs)(
        delayed(convert_runner)(fname, origin, i)
        for i, (origin, fname) in enumerate(samples)
    )

    core_vals = []
    ingredients = []
    for result in results:
        if result is not None:
            core_vals.append(result[0])
            ingredients.extend(result[1])

    if len(core_vals) == 0:
        print("No recipes parsed. Exiting.")
        return
    df_core = pd.DataFrame(core_vals)
    df_core = df_core.set_index("id")

    df_ing = pd.DataFrame(ingredients)
    df_ing = df_ing.set_index("id")
    clean_cols(df_ing)

    write_options = {"complevel": 9, "complib": "blosc", "format": "table"}
    if n == -1:
        fname = "interim/all_recipes.h5"
    else:
        # Calculate a filename as a hash of the xml files that were read in.
        fname = "interim/" + str(abs(hash(tuple(samples)))) + ".h5"
    fname = os.path.join(DATA_DIR, fname)
    print(f"Writing {len(samples)} examples to {fname}.")
    df_core.to_hdf(fname, "core", mode="w", data_columns=True, **write_options)
    df_ing.to_hdf(fname, "ingredients", mode="a", data_columns=True, **write_options)


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
        "times to specify multiple recipes to convert.",
    )
    parser.add_argument(
        "-n",
        "--number",
        type=int,
        default=20,
        help="If randomly parsing, number of recipes to randomly select for "
        "conversion. Note that -1 means to convert *all* recipes. Default "
        "is 20.",
    )
    parser.add_argument(
        "-j", "--jobs", type=int, default=N_CPUS, help="Number of processors to use."
    )
    return parser


if __name__ == "__main__":
    parser = _setup_argparser()
    args = parser.parse_args()

    convert_a_bunch(args.filename, args.number, args.jobs)
