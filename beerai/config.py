import os

# For use everywhere...
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.abspath(os.path.join(BASE, "data/"))
DOCS_DIR = os.path.abspath(os.path.join(BASE, "docs/"))
DOCS_IMAGES_DIR = os.path.abspath(os.path.join(DOCS_DIR, "assets/images"))

INGREDIENT_CATEGORIES = ["ferm", "hop", "yeast", "misc"]
