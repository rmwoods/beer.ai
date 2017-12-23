"""Parse out data from xml format."""

from lxml import etree

"""
RECIPES
 -RECIPE
  - ...

In [11]: root.findall("./RECIPE/*")
Out[11]: 
[<Element NAME at 0x7fae5d7ea308>,
 <Element STYLE at 0x7fae5d7a7408>,
 <Element FERMENTABLES at 0x7fae5d807608>,
 <Element HOPS at 0x7fae5d7e8a48>,
 <Element YEASTS at 0x7fae5d7e8848>,
 <Element MISCS at 0x7fae580da1c8>,
 <Element TYPE at 0x7fae580daa48>,
 <Element BREWER at 0x7fae580dad88>,
 <Element BATCH_SIZE at 0x7fae5d80bb88>,
 <Element BOIL_SIZE at 0x7fae5d80bbc8>,
 <Element BOIL_TIME at 0x7fae5d7d9648>,
 <Element EFFICIENCY at 0x7fae5d7d9608>]

"""


def parse_beer_recipe(recipe):
    """Given a beer recipe in XML format, parse out the relevant
    information into a dict."""
    try:
        root = etree.fromstring(recipe)[0]
    except IndexError:
        print("Empty Recipe.")
        return
    
    return

def parse_hops(hops):
    return

def parse_fermentables(ferm):
    return

def parse_yeast(yeast):
    return

def parse_misc(misc):
    return



