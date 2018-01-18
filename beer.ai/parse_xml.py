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

BASE = "./RECIPE/"

def parse_beer_recipe(recipe):
    """Given a beer recipe in XML format, parse out the relevant
    information into a dict."""
    try:
        root = etree.fromstring(recipe)
    except IndexError:
        print("Empty Recipe.")
        return
    
    try:
        eff_text = root.findall(BASE + "EFFICIENCY")[0].text
        eff = float(eff_text)
    except IndexError:
        # No efficiency specified - assume 1.0?
        eff = 1.0
    except ValueError:
        print("Bad efficiency format: {}".format(eff_text))
    try:
        boil_text = root.findall(BASE + "BOIL_SIZE")[0]
        boil_size = float(boil_text)
    except IndexError:
        # No boil_size specified - assume 1.0?
        boil_size = 1.0
    except ValueError:
        print("Bad boil size format: {}".format(boil_text))

    parse_hops(root.findall(BASE + "HOPS"))
    parse_fermentables(root.findall(BASE + "FERMENTABLES"))
    parse_yeast(root.findall(BASE + "YEAST"))
    parse_misc(root.findall(BASE + "MISC"))
    
    return

def parse_hops(hops):
    return

def parse_fermentables(ferm):
    return

def parse_yeast(yeast):
    return

def parse_misc(misc):
    return



