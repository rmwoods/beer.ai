"""Script to convert beer XMLs to a ML friendly format."""

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
ORIGIN_RE = "\((AF|AX|AL|DZ|AS|AD|AO|AI|AQ|AG|AR|AM|AW|AU|AT|AZ|BS|BH|BD|BB|BY|BE|BZ|BJ|BM|BT|BO|BQ|BA|BW|BV|BR|IO|BN|BG|BF|BI|KH|CM|CA|CV|KY|CF|TD|CL|CN|CX|CC|CO|KM|CG|CD|CK|CR|CI|HR|CU|CW|CY|CZ|DK|DJ|DM|DO|EC|EG|SV|GQ|ER|EE|ET|FK|FO|FJ|FI|FR|GF|PF|TF|GA|GM|GE|DE|GH|GI|GR|GL|GD|GP|GU|GT|GG|GN|GW|GY|HT|HM|VA|HN|HK|HU|IS|IN|ID|IR|IQ|IE|IM|IL|IT|JM|JP|JE|JO|KZ|KE|KI|KP|KR|KW|KG|LA|LV|LB|LS|LR|LY|LI|LT|LU|MO|MK|MG|MW|MY|MV|ML|MT|MH|MQ|MR|MU|YT|MX|FM|MD|MC|MN|ME|MS|MA|MZ|MM|NA|NR|NP|NL|NC|NZ|NI|NE|NG|NU|NF|MP|NO|OM|PK|PW|PS|PA|PG|PY|PE|PH|PN|PL|PT|PR|QA|RE|RO|RU|RW|BL|SH|KN|LC|MF|PM|VC|WS|SM|ST|SA|SN|RS|SC|SL|SG|SX|SK|SI|SB|SO|ZA|GS|SS|ES|LK|SD|SR|SJ|SZ|SE|CH|SY|TW|TJ|TZ|TH|TL|TG|TK|TO|TT|TN|TR|TM|TC|TV|UG|UA|AE|GB|US|UM|UY|UZ|VU|VE|VN|VG|VI|WF|EH|YE|ZM|ZW)\)"
N_CPUS = -1


def clean_text(text):
    """Standard method for cleaning text in our recipes. Any changes to parsing
    and storing text fields should happen here."""
    if text is not None:
        return text.lower().strip()


def check_origin(text):
    """Check a text object to see if 'origin' was included in it in the form of
    '(US)'. If so, return the original text object with that bit stripped, and
    the origin. Otherwise, return the original string and None."""
    origin = None
    mod_text = text
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


def recipe_to_df(recipe):
    """Given a pybeerxml.recipe.Recipe, convert to a dataframe and write in a
    more efficient format.
    """

    to_df = {}
    to_df["name"] = clean_text(recipe.name)
    to_df["batch_size"] = safe_float(recipe.batch_size)
    to_df["boil_size"] = safe_float(recipe.boil_size)


    for i, ferm in enumerate(recipe.fermentables):
        col = f"ferm{i}_"
        name, origin = check_origin(ferm.name)
        to_df[col + "name"] = clean_text(name)
        if origin is not None:
            to_df[col + "origin"] = clean_text(origin)
        else:
            to_df[col + "origin"] = clean_text(ferm.origin)
        to_df[col + "amount"] = safe_float(ferm.amount)

    for i, hop in enumerate(recipe.hops):
        col = f"hop{i}_"
        to_df[col + "name"] = clean_text(hop.name)
        to_df[col + "amount"] = safe_float(hop.amount)
        to_df[col + "alpha"] = safe_float(hop.alpha)
        to_df[col + "form"] = clean_text(hop.form)
        to_df[col + "time"] = safe_float(hop.time)

    for i, yeast in enumerate(recipe.yeasts):
        col = f"yeast{i}_"
        to_df[col + "name"] = clean_text(yeast.name)
        to_df[col + "laboratory"] = clean_text(yeast.laboratory)
        
    for i, misc in enumerate(recipe.miscs):
        col = f"miscs{i}_"
        to_df[col + "name"] = clean_text(misc.name)
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
    df = recipe_to_df(recipe)
    return df


def convert_a_bunch(path_to_recipes, n):
    """Convert n randomly chosen recipes. Currently for inspecting the output."""
    recipe_files = glob.glob(path.join(path_to_recipes, "*.xml"))
    samples = random.sample(recipe_files, n)

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
    df.to_hdf(fname, "test")


if __name__=="__main__":
    convert_a_bunch("recipes/", 20)
