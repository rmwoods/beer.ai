"""Convert the beerstyles2015 json files (from BJCP) to something easier to use."""
import json
import os

from beerai.config import DATA_DIR
# Format is as follows:
# styles = {"styleguide":
#              {"class": 
#                  [beer_guide, mead_guide, cider_guide]
#              }
#          }
#
# For each style guide (e.g. beer_guide):
# beer_guide = {'type': {...},
#             'introduction': {...},
#             'category': [cat1, cat2, ...]
#            }
#
# For each category (e.g. cat1):
# cat1 = {"id": 1,
#         "name": "Standard American Beer",
#         ...
#         "subcategory": [cat1_a, cat1_b],
#        }

# I think it makes sense to parse all the categories out as their own keys in a
# global dict, and make sure that if "subcategory" exists, to do the same for
# those.

def categories_to_dict(cat):
    """Given a category, convert it to a more manageable dict keyed on style
    id.
    """

    cat_id = cat.pop("id").lower()
    data = {cat_id: {}}
    for k,v in cat.items():
        data[cat_id][k] = v
    return data

def main():

    fname = os.path.join(DATA_DIR, "external/styleguide-2015.json")
    with open(fname ,"r") as f:
        # Format specified in comments at top of script
        styles = json.load(f)["styleguide"]["class"][0]["category"]

    converted = {}
    for style in styles:
        # Remove sub categories list
        sub_styles = style.pop("subcategory", [])
        # Add parent style
        converted.update(categories_to_dict(style))
        # Go through sub styles and add those
        for sub_style in sub_styles:
            converted.update(categories_to_dict(sub_style))
    
    fname = os.path.join(DATA_DIR, "processed/styleguide.json")
    with open(fname, "w") as f:
        json.dump(converted, f)

if __name__ == "__main__":
    main()
