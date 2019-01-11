import bs4
from pathlib import Path
import pickle
import re
import requests
import sys
import wget

# Brewtoad.com URLs: https://www.brewtoad.com/recipes?page=1&sort=created_at&sort_reverse=true

WEBSITE = "https://www.brewtoad.com"
URL = "https://www.brewtoad.com/recipes?page={}&sort=created_at&sort_reverse=true"
CHECKPOINT_FILE = "checkpoint.pickle"
R = re.compile("[0-9]+")

# Start by trying to load checkpoint file so we don't redo work.
try:
    with open(CHECKPOINT_FILE,"rb") as bf:
        stats = pickle.load(bf)
    start = stats["page"]+1
except FileNotFoundError:
    start = 1 

print("Starting on page {}".format(start))

# We do the first page outside of the loop to obtain the total number of pages
# that we'll need to loop over. Otherwise we don't know how long to loop.
request = requests.get(URL.format(start))
html = bs4.BeautifulSoup(request.text,"lxml")

pagination = html.find("div", attrs={"class": "pagination"})
n = re.findall(R, pagination.text)
if n:
    n_pages = int(n[-1])
else:
    print("Can't find pagination values.")
    sys.exit(1)

# Need to loop to n_pages+1 since the current loop is actually working on the
# nth-1 page.
for i in range(start+1, n_pages+1):
    recipes = html.find_all(name='li', attrs={"class":"recipe-container"})
    for recipe in recipes:
        sub = recipe.find("a", attrs={"class":"recipe-link"})
        address = sub.get("href")
        # The xml files are nicely named after the page they're from
        link = WEBSITE + address + ".xml"
        fname = "recipes/" + link.split("/")[-1]
        f = Path(fname)
        # If we don't already have this file, download it. This skips a recipe
        # if it has the same name as another recipe, but I'm not sure if that's
        # an issue worth trying to get around.
        if not f.is_file():
            wget.download(link, out=fname)
    print("Done page {}".format(i-1))
    # Checkpoint the page we finished so if we restart later, we continue from
    # the same page.
    with open(CHECKPOINT_FILE,"wb") as bf:
        pickle.dump({"page":i-1},bf)
    # Grab the new page
    request = requests.get(URL.format(i))
    html = bs4.BeautifulSoup(request.text,"lxml")

print("Done")
