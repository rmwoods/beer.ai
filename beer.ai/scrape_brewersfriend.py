import bs4
from pathlib import Path
import pickle
import re
import requests
import sys
import wget
import shutil
import pandas as pd

# Load checkpoint, set to increment

# Load recipe filename list 

# Iterate:
#   Start at current increment
#   Form the URL
#   Download the file 
#   Save checkpoint

WEBSITE = "https://www.brewersfriend.com"
URL = "https://www.brewersfriend.com/homebrew/recipe/beerxml1.0/"
CHECKPOINT_FILE = "checkpoint.pickle"
RECIPEPATH = "recipes_brewersfriend/"
USERAGENT = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

# Load the recipe CSV
recipe_df = pd.read_csv('recipeData.csv', encoding="ISO-8859-1")[['BeerID', 'URL']]
print('CSV loaded. Listing {} recipes.'.format(len(recipe_df)))

# Start by trying to load checkpoint file so we don't redo work.
try:
    with open(CHECKPOINT_FILE, "rb") as bf:
        stats = pickle.load(bf)
    start = stats["RecipeNumber"]+1
    print('Checkpoint loaded')
except FileNotFoundError:
    start = 0
    print('No checkpoint found. Starting from scratch')

i = 0
print('Current recipe number: {}'.format(i))

# Extract the Brewers' Friend recipe ID
recipe_page_URL = recipe_df['URL'][i]
recipe_id = re.search(r'/view/(.*?)/', recipe_page_URL).group(1)
print('Current Brewers Friend recipe ID: {}, page URL: {}'.format(str(recipe_id), recipe_page_URL))

# Form the BeerXML filename
recipe_XML_URL = URL + str(recipe_id) + '.xml'
print('Current Brewers Friend BeerXML URL: {}'.format(recipe_XML_URL))

# Download the recipe
fname = RECIPEPATH + recipe_XML_URL.split("/")[-1]
print('Filename: {}'.format(fname))
f = Path(fname)
# If we don't already have this file, download it. This skips a recipe
# if it has the same name as another recipe, but I'm not sure if that's
# an issue worth trying to get around.
if not f.is_file():
    #wget.download(recipe_XML_URL, out=fname)
    response = requests.get(recipe_XML_URL, headers=USERAGENT)

    with open(fname, 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)

    print('File downloaded. Path: {}'.format(fname))
else:
    print('File already downloaded. Skipping')

#
#     # Checkpoint the page we finished so if we restart later, we continue from
#     # the same page.
#     with open(CHECKPOINT_FILE,"wb") as bf:
#         pickle.dump({"page":i-1},bf)
#
#     # Grab the new page

#
# print("Done")
