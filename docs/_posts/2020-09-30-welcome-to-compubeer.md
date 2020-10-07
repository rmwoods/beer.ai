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
---

How do you teach a computer about beer?

Ideally, you pour it one. But as much as a CD tray looks like a coaster, that doesn't go well. In fact, without a few hundred thousand dollars of [equipment](https://en.wikipedia.org/wiki/Gas_chromatography), even giving your laptop an idea of what that beer tastes like is tricky. 

But you can tell your computer how a beer is made: there's a file format for that. [BeerXML](http://beerxml.com/) is a free standard for storing beer recipes in a computer-readable way. And with enough of these files, representing a large enough number of recipes, we can use data science tools to teach computers and ourselves about beer. 

**Compubeer** is a project to do just that, between 4 people who like numbers and beer. This first post is the starting point for these explorations: a discussion about our beer recipe dataset. We've assembled 400,000 homebrew beer recipes. Here's what that looks like.

# Where do recipes come from?
Who would write a beer recipe in a computer-readable format? Hundreds of thousands of people, it turns out. Or at least, they would in exchange for using a tool. BeerXML is the most popular export format for homebrew recipe sites. These sites give homebrewers a good reason to upload their recipes: they make it easy to store recipes, do calculations, record notes and share them. Here's a few examples:

| Site                                                                             | # Recipes       | Format  | Status  |
| -------------------------------------------------------------------------------- | --------------- | ------- | ------- |
| [Brewtoad](https://web.archive.org/web/20171231191610/https://www.brewtoad.com/) | 390,000+        | BeerXML | Defunct |
| [Brewer's Friend](https://www.brewersfriend.com/)                                | 190,000+        | BeerXML | Active  |
| [BeerSmith](http://beersmith.com/)                                               | 50,000+         | BeerXML | Active  |
| [BeerCalc](https://beercalc.org/)                                                | 150,000+        | Other   | Active  |
| [BrewGR](https://brewgr.com)                                                     | 60,000+         | Other   | Active  |


*But what about professional beer recipes?*

It would be wonderful to have a comprehensive picture of commercially-made beer recipes. Unfortunately that's a lot harder for a few reasons. Firstly, most professional brewers don't publish their recipes. This makes sense - they're trade secrets. So there is no public website for professional beer recipes. But secondly, it's also the case that there are fewer of them. In 2019 there were [8000+ breweries in the US](https://www.brewersassociation.org/statistics-and-data/national-beer-stats/) and [1100+ in Canada](https://industry.beercanada.com/statistics). This seems like a lot, but on Brewtoad alone there are recipes from **32,000+ brewers**.  Although looking to homebrewers does give a biased view on what a typical beer recipe looks like, it's necessary to get sample that's larger than a few dozen recipes. Also, it turns out this sample is less limited than you might think - several professional brewers actually upload their recipes to homebrew sites as well. 

# What recipes did we get?
In 2018 and 2019 we scraped:
* 330,790 recipes from [Brewtoad](https://web.archive.org/web/20171231191610/https://www.brewtoad.com/) 
* 72,367 recipes from [Brewer's Friend](https://www.brewersfriend.com/)
* 403,157 recipes in total

Since then, Brewtoad has gone defunct and its recipes are no longer available.

# What does a beer recipe look like in BeerXML?

As a brewer, you might see a recipe written down [like this](https://sierranevada.com/blog/pale-ale-homebrew-recipe/). There are some important measured quantites - fermentables and hops being the most obvious. There are also important ingredients whose quantities are up to the brewer, such as yeast or clarifying agents. And if you're a professional brewer, you'd also be looking for particulars such as fermentation temperature, pitch rate, aging schedule, target water composition, and plenty of other details.

BeerXML files can contain [plenty of these details](http://www.beerxml.com/beerxml.htm). However, only a small subset of tags are actually required, and we've found different sites include different sets of information. Amongst brewtoad and brewer's friend, recipes usually have at least the following tags:

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

In addition, where applicable, many of the `MISC` tags show up ("Raspberry Puree" is an example of a misc ingredient). From here, the next step is to read the consistent tags from the beerXML files into a data structure that we can start to work with in our modeling.

# 2) Dataset
We assembled a single dataset from our 400,000+ BeerXML files using [Pandas DataFrames](https://pandas.pydata.org/pandas-docs/stable/user_guide/dsintro.html).

We organized recipe data into DataFrames like this:
* Each recipe has a unique index number, `id`
* Two DataFrames use `id` as an index:
  * `core`, for quantities specific to a recipe 
    * *eg. boil size, batch size, boil time*
  * `ingredients`, for types and quantities relating to each ingredient addition in the recipe 
    * *eg. hop, malt, yeast, hops*

Here's an example of how those look, from a Brewtoad recipe for a Sierra Nevada Pale Ale clone:

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

  * Comment - can do some basic statistics on this
  * Comment - need to transform this for any sort of ML
* IBU, ABV, OG, FG, etc.
  * Included by some recipes, but we wrote our own functions... more later

# 3) Recipe Landscape

Now of course, anyone who has worked with data knows that a _huge_ part of data science is data cleanup, and this project is no exception. However, we're going to talk about our (very hefty) cleaning process in another post. So for now, let's start with some of the fun steps - digging in to see what we have!

How many recipes per style?

```python
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

Now of course, home brewers often start by cloning a favorite beer of theirs. What beers are cloned the most often? This is actually kind of a hard question to answer since we're relying on beer titles and text is inconsistent. Here's a first order estimate, anyway:

```python
>>> clones = core[core.name.str.contains("clone")]
>>> print(clones[:50])
pliny the elder              122
sierra nevada pale ale       114
zombie dust                  111
fat tire                      91
blue moon                     76
arrogant bastard              70
pliny                         62
stone ipa                     61
left hand milk stout          61
heady topper                  57
guinness                      51
oberon                        48
sierra nevada                 46
gumballhead                   46
two hearted                   46
lagunitas ipa                 43
hopslam                       42
snpa                          41
mirror pond                   41
moose drool                   40
founders breakfast stout      39
hoegaarden                    38
tank 7                        35
bell's two hearted            34
sculpin                       33
black butte porter            31
ruination                     31
anchor steam                  31
dead guy                      30
blind pig                     29
spotted cow                   29
kbs                           28
duvel                         28
old rasputin                  27
nugget nectar                 27
bell's two hearted ale        26
fuller's esb                  26
racer 5                       26
orval                         25
alaskan amber                 24
1554                          23
saison dupont                 23
celebration                   22
founders porter               22
fullers esb                   21
westvleteren 12               21
westy 12                      20
rochefort 8                   20
punk ipa                      19
magic hat #9                  19
```

Very cool! We're seeing some of the classics like Sierra Nevada's [Pale Ale](https://sierranevada.com/beer/pale-ale/) ("sierra nevada pale ale" and "snpa"), New Belgium's [Fat Tire Amber Ale](https://www.newbelgium.com/beer/fat-tire/), and [Blue Moon](https://www.bluemoonbrewingcompany.com/currently-available/blue-moon-belgian-white)'s (presmably) Belgian White. We're also seeing some of the ["Whales"](https://www.eater.com/drinks/2015/2/20/8077349/the-white-while-the-most-elusive-craft-beers) (XXX what to link to here?) of the brewing world like Russian River Brewing's [Pliny The Elder](https://russianriverbrewing.com/pliny-the-elder/), The Alchemist's [Heady Topper](https://alchemistbeer.com/), and even a few clones for Westvleteren's [Westy 12](https://en.wikipedia.org/wiki/Westvleteren_Brewery)'s. What clones have you made?


* What does the beer recipe landscape look like
  * most common malt, hop, yeast names
  * batch sizes
* Sneak preview: beer measurables (IBU, ABV, SRM)

# 4) What Next?
* Roadmap:
  * Recipe analysis
  * Recipe generation
* Link to app 

{% if page.notebook_src %}
  {% include {{ page.notebook_src }} %}
{% endif %}
