# beer.ai
Using Machine Learning to generate new beers.

This project is a fun attempt to create beer recipes based on learning other recipes from online sources.

# Getting Started

Getting your environment set up is standard. Note that this project requires python3.6+.

```bash
python3.6 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

Once installed, you're good to go. Note that there is currently an annoying print statement in the pybeerxml package. You can get rid of it by deleting line 22 in `.env/lib/python3.6/site-packages/pybeerxml/fermentable.py`.

After this, you need data. Currently, you can either run the web scraper to get your own data (takes days), or you can ask Rory for the data. It should be stored in `beer.ai/recipes/*.xml`. As soon as we have finished pre-processing the recipes, you can likely skip this step and just load up an HDF containing all the recipes.

# Project Layout

This will be filled in more at the end.

* `beer.ai` contains the primary code, at the moment.
* `beer.ai/recipes` contains all the beer xml recipe files
* ...

# Recipe Assumptions

Most of the assumptions about how we handle a recipe are stored in `sequence_notes.md`. This mentions what fields we're using, where we're normalizing values, and the general procedure of how we create a recipe from a beer xml file.

# Authors

- Rory Woods
- Rob Welch