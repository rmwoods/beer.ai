---
layout: single
title: Our dataset
author: everyone
read_time: false
draft: false
header:
  image: /assets/images/bells_kettle.png
  teaser: /assets/images/bells_kettle.png
  caption: Boil kettle, Bell's
gallery:
  - url: /assets/images/fermentable_wordcloud.png
    image_path: /assets/images/fermentable_wordcloud.png
    alt: "Fermentable wordcloud"
    title: "The most common fermentables in our recipes."
  - url: /assets/images/hops_wordcloud.png
    image_path: /assets/images/hops_wordcloud.png
    alt: "Hops wordcloud"
    title: "The most common hops in our recipes."
  - url: /assets/images/yeast_wordcloud.png
    image_path: /assets/images/yeast_wordcloud.png
    alt: "Yeast wordcloud"
    title: "The most common yeasts in our recipes."
---

How do you teach a computer about beer?

Ideally, you pour it one. But as much as a CD tray looks like a coaster, that doesn't go well. In fact, without a few hundred thousand dollars of [equipment](https://en.wikipedia.org/wiki/Gas_chromatography), even giving your laptop an idea of what that beer tastes like is tricky. 

But you can tell your computer how a beer is made: there's a file format for that. [BeerXML](http://beerxml.com/) is a free standard for storing beer recipes in a computer-readable way. And with enough of these files, representing a large enough number of recipes, we can use data science tools to teach computers and ourselves about beer. 

**Compubeer** is a project by a group of people who like both numbers and beer. We've assembled over 400,000 homebrew beer recipes. Here's what that looks like.

# Where do these recipes come from?

The modern homebrewing community makes extensive use of online tools for
recipe creation, tracking their brew process, and sharing with others.
Here are the most popular online tools (with recipe counts as of October 2020).

| Site                                                                             | # Recipes       | Format  | Status  |
| -------------------------------------------------------------------------------- | --------------- | ------- | ------- |
| [Brewtoad](https://web.archive.org/web/20171231191610/https://www.brewtoad.com/) | 390,000+        | BeerXML | Defunct |
| [Brewer's Friend](https://www.brewersfriend.com/)                                | 190,000+        | BeerXML | Active  |
| [BeerSmith](http://beersmith.com/)                                               | 50,000+         | BeerXML | Active  |
| [BeerCalc](https://beercalc.org/)                                                | 150,000+        | Other   | Active  |
| [BrewGR](https://brewgr.com)                                                     | 60,000+         | Other   | Active  |


These online tools represent a large repository of user-contributed beer
recipe information. Getting a similar volume of recipes for commercial 
beers would be much more difficult if not impossible!
Consider that in 2019 there were [8000+ breweries in the US](https://www.brewersassociation.org/statistics-and-data/national-beer-stats/) and [1100+ in Canada](https://industry.beercanada.com/statistics), whereas on Brewtoad alone there are recipes from **32,000+ brewers**. It is our hope that this diversity
will be a strength, despite most recipes coming from homebrewers rather than
pros. 

# What recipes did we get?

In 2018 and 2019 we scraped:
* 330,790 recipes from [Brewtoad](https://web.archive.org/web/20171231191610/https://www.brewtoad.com/) 
* 72,367 recipes from [Brewer's Friend](https://www.brewersfriend.com/)
* 403,157 recipes in total

Since then, Brewtoad has gone defunct and its recipes are no longer available.

# What does a beer recipe look like in BeerXML?

As a brewer, you might see a recipe written down [like this](https://sierranevada.com/blog/pale-ale-homebrew-recipe/). There are some important measured quantites - fermentables and hops being the most obvious. There are also important ingredients whose quantities are up to the brewer, such as yeast or clarifying agents. There are also particulars such as fermentation temperature, pitch rate, aging schedule, target water composition, and other details.

BeerXML files can contain [plenty of these details](http://www.beerxml.com/beerxml.htm). However, only a small subset of tags are actually required, and we've found that different websites include different sets of information. These are the tags in common between Brewtoad and Brewer's Friend.

|:---:|---|:---:|---|
| **Style** | ABV\_MAX | **Recipe** | BATCH\_SIZE |
|  | ABV\_MIN |  | BOIL\_SIZE |
|  | CATEGORY\_NUMBER |  | BOIL\_TIME |
|  | COLOR\_MAX |  | BREWER |
|  | COLOR\_MIN |  | EFFICIENCY |
|  | FG\_MAX |  | NAME |
|  | FG\_MIN |  | TYPE |
|  | IBU\_MAX |  |  |
|  | IBU\_MIN |  |  |
|  | NAME |  |  |
|  | OG\_MAX |  |  |
|  | OG\_MIN |  |  |
|  | STYLE\_GUIDE |  |  |
|  | STYLE\_LETTER |  |  |
|  | TYPE |  |  |
|  | VERSION |  |  |
| **Fermentables** | ADD\_AFTER\_BOIL | **Hops** | ALPHA |
|  | AMOUNT |  | AMOUNT |
|  | COLOR |  | FORM |
|  | NAME |  | NAME |
|  | ORIGIN |  | TIME |
|  | TYPE |  | USE |
|  | YIELD |  |  |

In addition, where applicable, many of the `MISC` tags show up ("Raspberry Puree" is an example of a misc ingredient). We read these common tags from the beerXML files into a data structure that we can use for subsequent analysis of these recipes.

# How do we store the recipes?

We assembled a single dataset from our 400,000+ BeerXML files using [Pandas DataFrames](https://pandas.pydata.org/pandas-docs/stable/user_guide/dsintro.html).

We organized the recipes into DataFrames like this:
* Each recipe has a unique index number, `id`
* Two DataFrames share that `id` as an index:
  * `core`, for recipe-level data
    * *eg. boil size, batch size, boil time*
  * `ingredients`, for ingredient-level data
    * *eg. hops, malt, and yeast*

Here's an example from a real recipe, for a Sierra Nevada Pale Ale clone from Brewtoad:

### `core`: recipe details

|      id | batch_size | boil_size | boil_time | efficiency | name      | style_name        | origin   |
| ------- | ---------- | --------- | --------- | ---------- | --------- | ----------------- | -------- |
| 258754  |    20.820… |   26.498… |        60 |       0.75 | snpaclone | american pale ale | brewtoad |

### `ingredients`: fermentables

|      id | ferm_name   | ferm_origin | ferm_type            | ferm_yield | ferm_amount | ferm_color |
| ------- | ----------- | ----------- | -------------------- | ---------- | ----------- | ---------- |
| 258754  | 2-row       | us          | base malt            |     0.799… |      4.536… |          1 |
| 258754  | crystal 40l | ca          | caramel/crystal malt |     0.734… |      0.454… |         40 |

### `ingredients`: hops

|      id | hop_name | hop_origin | hop_amount | hop_form | hop_time | hop_use |
| ------- | -------- | ---------- | ---------- | -------- | -------- | ------- |
| 258754  | perle    | us         |     0.028… | pellet   |       60 | boil    |
| 258754  | cascade  | us         |     0.028… | pellet   |       15 | boil    |
| 258754  | cascade  | us         |     0.028… | pellet   |        0 | boil    |
| 258754  | cascade  | us         |     0.028… | pellet   |    7,200 | dry hop |

### `ingredients`: yeast

|      id | yeast_name   | yeast_form | yeast_amount | yeast_attenuation |
| ------- | ------------ | ---------- | ------------ | ----------------- |
| 258754  | safale us-05 | dry        |          NaN |              85.5 |


These numbers give a basic, simplified idea of what goes into a beer. They're enough to brew it with some educated guesses.
They give good detail on the ingredients: 
* The name and quantity of each ingredient
* The yield and colour of each fermentable
* The time and alpha acid of each hop addition

As well as some basics about process:
* The batch-specific parameters necessary to adjust to your brewhouse (batch and boil size, efficiency)

But we're left to our own judgement to fill in most of the details to do with process:
* Brewhouse (grist to liquor ratio, mash temperature(s), sparge volumes)
* Fermentation (pitch rate, oxygenation, temperature)

Also worth noting is the absense of **target measurements**! We'll have to write our own formulas to calculate the numbers we're used to seeing on beer labels (we'll go over these calculations in another post):
* ABV (as well as OG and FG)
* IBU
* SRM

# What are homebrewers making? What ingredients are they using?

Stay tuned for details on our (very hefty) data cleaning process in a future post.
In the meantime, we can answer some simple but fun questions.

How many recipes do we have per style?

```
>>> core.groupby("style_name").name.agg("count").sort_values(ascending=False)
style_name
american ipa                                      59702
american pale ale                                 45597
specialty beer                                    28314
imperial ipa                                      15595
saison                                            15289
american amber ale                                11842
american brown ale                                 9547
robust porter                                      9492
american wheat or rye beer                         8955
russian imperial stout                             8619
blonde ale                                         7838
weizen/weissbier                                   7483
american stout                                     7403
extra special/strong bitter (english pale ale)     6732
witbier                                            6285
irish red ale                                      6208
sweet stout                                        5976
oatmeal stout                                      5942
belgian specialty ale                              5112
spice, herb, or vegetable beer                     4737
cream ale                                          4714
kölsch                                             4195
english ipa                                        4115
fruit beer                                         3754
oktoberfest/märzen                                 3703
belgian tripel                                     3611
belgian dubbel                                     3333
belgian dark strong ale                            3330
dry stout                                          3286
american barleywine                                3110
belgian pale ale                                   3040
california common beer                             3001
belgian blond ale                                  2984
brown porter                                       2904
german pilsner (pils)                              2890
strong scotch ale                                  2748
mild                                               2594
bohemian pilsener                                  2452
northern english brown ale                         2381
special/best/premium bitter                        2372
christmas/winter specialty spiced beer             2357
belgian golden strong ale                          2355
american light lager                               2146
dunkelweizen                                       2066
baltic porter                                      2020
old ale                                            1990
berliner weisse                                    1873
standard/ordinary bitter                           1832
vienna lager                                       1748
foreign extra stout                                1611
english barleywine                                 1547
scottish export 80/-                               1454
munich helles                                      1382
maibock/helles bock                                1333
doppelbock                                         1316
düsseldorf altbier                                 1211
classic american pilsner                           1166
weizenbock                                         1164
other smoked beer                                  1119
premium american lager                             1079
schwarzbier (black beer)                           1069
lite american lager                                1023
munich dunkel                                       969
weissbier                                           969
flanders red ale                                    950
bière de garde                                      941
double ipa                                          834
traditional bock                                    770
american porter                                     761
roggenbier (german rye beer)                        759
wood-aged beer                                      736
imperial stout                                      668
extra special/strong bitter (esb)                   658
american wheat beer                                 647
specialty ipa: black ipa                            616
southern english brown                              605
no profile selected                                 589
flanders brown ale/oud bruin                        552
fruit lambic                                        536
dark american lager                                 487
northern german altbier                             473
strong bitter                                       465
standard american lager                             457
specialty ipa: red ipa                              439
straight (unblended) lambic                         421
experimental beer                                   420
scottish heavy 70/-                                 417
british brown ale                                   381
best bitter                                         381
gueuze                                              373
dortmunder export                                   350
classic rauchbier                                   343
märzen                                              331
holiday/winter special spiced beer                  327
specialty ipa: rye ipa                              313
international pale lager                            302
northern english brown                              284
scottish light 60/-                                 275
specialty ipa: white ipa                            274
ordinary bitter                                     262
british golden ale                                  260
irish stout                                         259
dark mild                                           238
czech premium pale lager                            236
american lager                                      223
american strong ale                                 222
english porter                                      217
specialty ipa: belgian ipa                          214
schwarzbier                                         213
german pils                                         199
dunkles weissbier                                   195
british strong ale                                  190
scottish export                                     176
mixed-fermentation sour beer                        160
czech pale lager                                    159
california common                                   151
winter seasonal beer                                151
gose                                                146
clone beer                                          137
altbier                                             137
mixed-style beer                                    136
wee heavy                                           136
trappist single                                     121
eisbock                                             106
scottish heavy                                      105
braggot                                              92
common cider                                         91
specialty ipa: brown ipa                             89
international amber lager                            88
dry mead                                             79
autumn seasonal beer                                 76
helles bock                                          73
light american lager                                 73
lambic                                               70
north german altbier                                 68
specialty smoked beer                                67
specialty ipa: new england ipa                       66
brett beer                                           64
classic style smoked beer                            64
irish extra stout                                    62
other fruit melomel                                  62
festbier                                             61
specialty fruit beer                                 51
australian sparkling ale                             46
semi-sweet mead                                      45
dunkles bock                                         44
wheatwine                                            44
wild specialty beer                                  44
rauchbier                                            43
scottish light                                       41
sweet mead                                           37
fruit and spice beer                                 36
other specialty cider or perry                       35
czech dark lager                                     33
alternative grain beer                               33
international dark lager                             32
roggenbier                                           31
oud bruin                                            30
german helles exportbier                             30
english cider                                        30
czech amber lager                                    30
kentucky common                                      29
pre-prohibition lager                                29
tropical stout                                       28
fruit cider                                          22
sahti                                                22
alternative sugar beer                               20
german leichtbier                                    19
kellerbier: pale kellerbier                          19
open category mead                                   17
cyser (apple melomel)                                17
kellerbier: amber kellerbier                         16
piwo grodziskie                                      16
metheglin                                            14
specialty wood-aged beer                             12
pre-prohibition porter                               12
london brown ale                                      8
new england cider                                     7
lichtenhainer                                         6
apple wine                                            6
pyment (grape melomel)                                5
traditional perry                                     2
french cider                                          2
burton ale                                            1
```

Cloning commercial beers is one way that pro(-ish) recipes are included in the data. What beers are cloned the most often? Judging only by beer recipe names, we can get a general picture:

[![Clones wordcloud](/assets/images/clones_wordcloud.png)](/assets/images/clones_wordcloud.png)

Very cool! We're seeing some of the classics like Sierra Nevada's [Pale Ale](https://sierranevada.com/beer/pale-ale/) ("sierra nevada pale ale" and "snpa"), New Belgium's [Fat Tire Amber Ale](https://www.newbelgium.com/beer/fat-tire/), and [Blue Moon](https://www.bluemoonbrewingcompany.com/currently-available/blue-moon-belgian-white)'s (presumably) Belgian White. We're also seeing some of the ["Whales"](https://www.eater.com/drinks/2015/2/20/8077349/the-white-while-the-most-elusive-craft-beers) of the brewing world like Russian River Brewing's [Pliny The Elder](https://russianriverbrewing.com/pliny-the-elder/), The Alchemist's [Heady Topper](https://alchemistbeer.com/), and even a few clones for Westvleteren's [Westy 12](https://en.wikipedia.org/wiki/Westvleteren_Brewery)'s.

What about ingredients? That is, after all, one of the most special aspects of this data set. While we'll do plenty of analysis on this later on, let's start with a simple question: what are the most common ingredients in each of fermentables, hops, and yeasts?

{% include gallery caption="The most common ingredients in our recipes." %}

As expected from our most common styles and clones, we see the most common fermentable is 2-row, the most common hop is cascade, and the most common yeast is Safale US-05.

These are just about the simplest questions we can ask about our beer recipe landscape. By calculating characteristics like IBU, ABV, and SRM, we can go one step further. As a teaser, we created a [fun little visualization tool]({% link _apps/ibu_abv_color.md %}) to explore beer styles by their position in the IBU-ABV-SRM space.

# What Next?

We're planning to continue exploring our recipes to answer interesting questions, such as:

* What differentiates a stout and a porter?
* What ingredients define particular styles?
* How do beer styles empirically compare to their BJCP definitions?

Not only this, we'll be making more apps that let you do things like:

* Generate a completely AI-based recipe (or AI-assisted if you want to start with a certain set of ingredients)
* Analyze recipes - how does your recipe compare to all of the others in the dataset?
* Hybridize recipe - how do I make a style X - style Y hybrid that retains the most defining characteristics of each style?

Until next time - Cheers!
