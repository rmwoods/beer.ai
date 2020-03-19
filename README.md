# beer.ai
Using Machine Learning to generate new beers.

This project is a fun attempt to create beer recipes based on learning other recipes from online sources.

# Getting Started

Getting your environment set up is standard. Note that this project requires python3.6+.

```bash
python3.6 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

Once installed, you're good to go. Note that there is currently an annoying print statement in the pybeerxml package. You can get rid of it by deleting line 22 in `.env/lib/python3.6/site-packages/pybeerxml/fermentable.py`.

After this, you need data. Currently, you can either run the web scraper to get your own data (takes days), or you can ask Rory for the data. It should be stored in `beer.ai/recipes/*.xml`. As soon as we have finished pre-processing the recipes, you can likely skip this step and just load up an HDF containing all the recipes.

# Project Layout

This will be filled in more at the end.

* `beer.ai` contains the primary code, at the moment.
* `beer.ai/recipes` contains all the beer xml recipe files
* ...

# Data and Formats

There are a number of files containing useful data available for this project. The list below describes what is contained in each file.

* `all_recipes.h5` - Raw recipe data in HDF5 format. Contains every recipe entry that has been parsed from beer xml files. The recipes are split into 2 tables:
  * `core` - A table containing the core information about a recipe. The index of this table is a unique identifier for the recipe, and matches with the `ingredients` table entries.
  * Fields:

Name | Description | Unit | Data type | Typical values
--- | --- | --- | --- | ---
`batch_size` | The volume in the fermenter, pre-fermentation. Or the volume in the package (bottle/keg). Depending on who you ask :) | litres | float64 | 19.684141256, 18.927059, 22.712471  
`boil_size` | | | | 
`boil_time` | | | | 
`brewer` | | | | 
`efficiency` | | | | 
`fg` | | | | 
`ibu` | | | | 
`name` | | | | 
`og` | | | | 
`origin` | | | | 
`recipe_file` | | | | 
`style_category` | | | | 
`style_name` | | | | 
`style_version` | | | | 

  * `ingredients` - A table containing the actual ingredients for each recipe. The index of this table matches with the index from the `core` table. Note that a given recipe can (and usually does) span multiple rows since a given row holds only one of each type of ingredient (see below) and there will usually be multiples of each type of ingredient.
    * `ferm_amount`, `ferm_color`, `ferm_display_amount`, `ferm_name`, `ferm_origin`, `ferm_potential`, `ferm_yield`.
    * `hop_alpha`, `hop_amount`, `hop_display_amount`, `hop_form`, `hop_name`, `hop_origin`, `hop_time`, `hop_use`.
    * `misc_amount`, `misc_amount_is_weight`, `misc_name`, `misc_time`, `misc_use`.
    * `yeast_amount`, `yeast_attenuation`, `yeast_flocculation`, `yeast_form`, `yeast_laboratory`, `yeast_name`, `yeast_product_id`, `yeast_type`
* `recipe_vecs.h5` - A representation of recipes in a simple format.
  * The data is stored under the `vecs` key.
  * Each recipe is represented as an (N+1) length vector, where N is the number of possible ingredients (similar to [one-hot encodings](https://en.wikipedia.org/wiki/One-hot)). The index in each vector represents a specific ingredient, and the value in that index represents how much of that ingredient is present (in mass/liter units).
  * The last entry in each recipe vector represents the boil time in minutes. This is the `+1` above.
  * The lookup for indice-to-ingredient is present in `vocab.pickle` (see below).
* `vocab.pickle` - A mapping of ingredient string -> unique id.
  * The map is stored as a simple python dict going from str -> int.
  * The unique id's in this map indicate the index of the vector in the `recipe_vecs` representation of recipes (see above) that will have a value.
* `*map.pickle` - A mapping of various ingredient strings to the "standard" version of that string.
  * The `*` above can be replaced with any of the ingredient categories (ferm, hop, misc, yeast).
  * The "standard" version is usually either a less specific version of an ingredient (e.g. "Munton's roasted barley" -> "roasted barley"), a symbol-standard version ("2-row" -> "2 row"), or a properly-spelled version (e.g. "veinna malt" -> "vienna malt").
  * The maps have been painstakingly created by hand and represent our best (first) effort to standardize ingredients. There are a lot of assumptions that get built into this process. For a discussion on this, see XXX.

# Loading in Data

This section gives information on how to read in recipes, manipulate them, and make sense of the data.

## Raw Recipes

Loading in raw recipes is fairly straightforward with pandas.

```python
import pandas as pd

store = pd.HDFStore("all_recipes.h5", "r")

# Read in recipes 10-20. "start"/"stop" says how many rows to read
recipes = store.select("/core", start=10, stop=20)

# Read in the ingredients for the first 10 recipes. "where" says which indices
# to pull out, which is not the same as the number of rows in the `ingredients`
# table.
ingredients = store.select("/ingredients", where="index >= 10 & index < 20")

# Join the dataframes together. Note that this will duplicate the information
# in `recipes` to match the number of rows in ingredients. For other ways of
# joining, look at the pandas documentation for `join` and `merge`.
df = recipes.join(ingredients)
```

The above example will load in the raw recipes, which is mostly just useful for inspecting the various data columns and doing exploratory data analysis (EDA) on the base quantities.

If you wanted to "standardize" (see "Data and Formats" above) all of the ingredients for a particular category, you could do the following (starting with `ingredients` from above):

```python
import pickle

# Standardize our fermentables
with open("fermmap.pickle","rb") as f:
    fermmap = pickle.load(f)

ingredients["ferm_name"].replace(fermmap, inplace=True)
```

## Simple Recipe Vector Representation

To play around with the simple recipe representation, you can do the following:

```python
with pd.HDFStore("recipe_vecs.h5","r") as store:
    vecs = store.get("/vecs")
vecs.shape
# (171699, 793)
```
In the above example, we see that we have 171,699 recipes that are each represented as a length 793 vector. This could be translated to an english-reading recipe with the following code:

```python
with open("vocab.pickle", "rb") as f:
    vocab = pickle.load(f)

# Change from str -> int to int -> str
inv_vocab = {v:k for k,v in vocab.items()}

# Look at first recipe
rec1 = vecs.iloc[0]
rec1[rec1 != 0].reset_index().replace({"name": inverse_vocab})

#                           name        0.0
# 0              ferm_flaked rice   0.011782
# 1  yeast_brettanomyces lambicus   0.052674
# 2          yeast_east coast ale   0.024258
# 3         yeast_fermentis us-05   0.013862
# 4                     hop_comet   1.000000
# 5                    hop_waimea   0.000193
# 6                    boil_time   60.000000
```


# Recipe Assumptions

Most of the assumptions about how we handle a recipe are stored in `sequence_notes.md`. This mentions what fields we're using, where we're normalizing values, and the general procedure of how we create a recipe from a beer xml file.

# Authors

- Rory Woods
- Rob Welch
