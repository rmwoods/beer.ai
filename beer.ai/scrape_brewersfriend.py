import bs4
from pathlib import Path
import pickle
import re
import requests
import sys
import wget
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

# Load recipe CSV
recipe_df = pd.read_csv('recipeData.csv', encoding = "ISO-8859-1")[['BeerID', 'URL']]
# Extract the Brewers' Friend recipe ID
s = recipe_df['URL'][0]
recipe_id = re.search(r'/view/(.*?)/', s).group(1)

# Start by trying to load checkpoint file so we don't redo work.
try:
    with open(CHECKPOINT_FILE,"rb") as bf:
        stats = pickle.load(bf)
    start = stats["page"]+1
    
except FileNotFoundError:
    start = 1 

    # Checkpoint the page we finished so if we restart later, we continue from
    # the same page.
    with open(CHECKPOINT_FILE,"wb") as bf:
        pickle.dump({"page":i-1},bf)
        
    # Grab the new page
    request = requests.get(URL.format(i))
    html = bs4.BeautifulSoup(request.text,"lxml")

print("Done")
