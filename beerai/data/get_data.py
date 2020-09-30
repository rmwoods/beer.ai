"""Download required data files for the project."""
import os
import zipfile

from dotenv import load_dotenv, find_dotenv

_dotenv_path = find_dotenv()
load_dotenv(_dotenv_path)

DROPBOX_TOKEN = os.environ.get("DROPBOX_TOKEN")


def get_recipe_xmls():
    #dbx.files_download_to_file(..., beer/brewtoad_recipes.zip)
    #dbx.files_download_to_file(..., beer/brewersfriend_recipes.zip)
    #unzip to appropriate directories
    pass


def get_all_recipes():
    #dbx.files_download_to_file(..., beer/allrecipes.h5)
    pass


def get_ingredient_maps():
    #dbx.files_download_to_file(..., beer/fermmap.pickle)
    #dbx.files_download_to_file(..., beer/hopmap.pickle)
    #dbx.files_download_to_file(..., beer/yeastmap.pickle)
    #dbx.files_download_to_file(..., beer/miscmap.pickle)
    pass


def get_recipe_vectors():
    #dbx.files_download_to_file(..., beer/recipe_vecs.h5)
    pass


def main():
    # XXX - these functions need to be filled in and tested. Currently
    # developing in remote area, don't want to use bandwidth.

    dbx = dropbox.Dropbox(DROPBOX_TOKEN)

    get_recipe_xmls(dbx)
    get_all_recipes(dbx)
    get_ingredient_maps(dbx)
    get_recipe_vectors(dbx)


if __name__ == "__main__":
    main()
