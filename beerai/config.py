import os

# For use everywhere...
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.abspath(os.path.join(BASE, "data/"))
SUPPORT_DIR = os.path.abspath(os.path.join(BASE, "beerai/supporting_files/"))

VALID_CATEGORIES = ["ferm", "hop", "yeast", "misc"]

