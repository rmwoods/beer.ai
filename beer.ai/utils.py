import json


def get_style_guide():
    with open("styleguide.json") as f:
        style_guide = json.load(f)


def ibu(df):
    """Return an estimated IBU given a beer recipe.

    Parameters:
    ===========
        hops: dataframe
            Dataframe containing scaled hop quantities and addition times.
            Assumed columns are "hop_scaled", "hop_time"
    Return:
    ======
        IBU: float
        Estimate of the IBU for this set of hops (presumably corresponding to a
        recipe.
    """
    pass


def srm():
    """
    """
    pass


def color(*args, **kwargs):
    return srm(*args, **kwargs)


def abv():
    pass
