import json

with open("../supporting_files/styleguide-2015.json","r") as f:
    styles = json.load(f)

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

def category_to_dict(cat):
    cat_id = cat.pop("id")
