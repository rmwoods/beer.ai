import bs4
import re
import requests
import sys
import wget

# Brewtoad.com URLs: https://www.brewtoad.com/recipes?page=1&sort=created_at&sort_reverse=true

WEBSITE = "https://www.brewtoad.com"
URL = "https://www.brewtoad.com/recipes?page={}&sort=created_at&sort_reverse=true"

request = requests.get(URL.format(1))
html = bs4.BeautifulSoup(request.text)

r = re.compile("[0-9]+")
pagination = html.find("div",attrs={"class":"pagination"})
n = re.findall(r,pagination.text)
if n:
    n_pages = int(n[-1])
else:
    print("Can't find pagination values.")
    sys.exit(1)

for i in range(2,n_pages-1):
    recipes = html.find_all(name='li',attrs={"class":"recipe-container"})
    for recipe in recipes:
        sub = recipe.find("a",attrs={"class":"recipe-link"})
        address = sub.get("href")
        link = WEBSITE + address + ".xml"
        fname = link.split("/")[-1]
        wget.download(link,out="recipes/"+fname)
    request = requests.get(URL.format(i))
    html = bs4.BeautifulSoup(request.text)

print("Done")
