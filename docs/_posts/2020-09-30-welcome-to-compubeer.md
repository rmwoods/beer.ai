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

Here's an example of what recipe data we have available and how it looks. (These are from a real recipe, for Sierra Nevada Pale Ale clone from Brewtoad):

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

But we're left to our own judgement to fill in most of the process details:
* Mash (grist to liquor ratio, mash temperature(s), )
* Fermentation (pitch rate, oxygenation, temperature)

Also worth noting is the absense of **target measurements**! We'll have to write our own formulas to calculate:
* ABV (as well as OG and FG)
* IBU
* SRM
(Spoiler: we did)

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

What about ingredients? That is, after all, one of the most special aspects of this data set. While we'll do plenty of analysis on this later on, let's start with a simple question: what are the most common ingredients in each of fermentables, hops, and yeasts?

First, fermentables:

```
2-row                           182624
pilsen malt                      76485
carapils® malt                   70712
white wheat                      66763
caramel/crystal 60l              65671
maris otter pale                 55600
caramel malt 40l                 51434
roasted barley                   43401
flaked oats                      42731
dry malt extract - light         40349
vienna                           39865
chocolate malt                   34444
liquid malt extract - light      34401
munich malt                      33850
chocolate                        33824
caramel malt 20l                 31473
caramel malt 120l                30474
caramel malt 80l                 27799
black malt                       26567
flaked wheat                     24530
munich malt 10l                  24255
victory® malt                    23014
special b                        22431
caramel malt 10l                 21377
corn sugar (dextrose)            20527
honey malt                       20209
biscuit® md™                     20133
aromatic barley malt             18286
flaked barley                    16834
acidulated malt                  13003
melanoidin                       11755
dry malt extract - pilsen        11350
pale chocolate                   11038
munich light                     10597
rye                               9756
honey                             9720
golden promise                    9277
dry malt extract - wheat          9158
rice hulls                        8801
liquid malt extract - pilsen      8760
flaked corn                       8438
liquid malt extract - amber       8254
sugar, table (sucrose)            8158
6-row                             8146
carared                           8127
dry malt extract - amber          7921
dark munich                       7748
brown malt                        7648
candi sugar, clear                7293
caramunich i                      7266
```

Hops...

```
cascade                   91148
centennial                50993
east kent golding         49612
citra                     43659
amarillo                  42270
columbus                  37940
simcoe                    35402
chinook                   34627
saaz                      34032
willamette                33842
magnum                    33416
fuggle                    32692
hallertau                 31963
northern brewer           23779
tettnanger                17670
warrior                   16663
nugget                    16317
mosaic™                   13943
perle                     13484
styrian golding           12927
galaxy                    10141
mount hood                 9431
nelson sauvin              8151
summit                     7860
hallertauer mittelfrüh     7538
challenger                 7430
galena                     6750
cluster                    6682
hersbrucker                6211
liberty                    5752
crystal                    5718
sorachi ace                5077
sterling                   4816
strisselspalt              4625
falconer's flight          4526
ahtanum                    4348
target                     4104
motueka                    4071
glacier                    3645
horizon                    3240
brewers gold               3171
apollo                     3149
palisade                   3103
el dorado                  3079
bravo                      2854
zythos                     2516
pacific gem                2088
calypso                    1836
pacific jade               1835
bramling cross             1810
```

and yeasts:

```
safale us-05                       51247
american ale                       22138
american ale ii                    19856
safale s-04                        18634
french saison                       6062
london ale iii                      5690
london esb ale                      5120
california lager                    4462
scottish ale                        4152
irish ale                           3958
weihenstephan weizen                3897
california ale                      3766
belgian abbey ii                    3262
belgian ale                         3192
belgian wit ale                     3158
fermentis us-05                     3012
german ale                          2932
british ale                         2812
safbrew t-58                        2802
london ale                          2635
denny's favorite 50                 2528
saflager w-34/70                    2487
trappist high gravity               2458
northwest ale                       2456
safbrew wb-06                       2371
saflager s-23                       2275
american wheat                      2139
safbrew s-33                        2126
kölsh                               1961
nottingham ale                      1960
belle saison                        1915
british ale ii                      1850
bohemian lager                      1773
vermont ale                         1735
brettanomyces bruxellensis          1684
bavarian lager                      1678
thames valley ale                   1541
ringwood ale                        1229
whitbread ale                       1096
u.s. west coast                     1090
belgian strong ale                  1081
munich lager                        1075
roeselare ale blend                 1066
kolsch (2565)                       1064
bavarian wheat                       940
super high gravity ale (wlp099)      856
bavarian wheat blend                 836
lactobacillus                        815
german wheat                         804
west yorkshire (1469)                787
```

These are just about the simplest questions we can ask about our beer landscape. But it gets a bit more interesting and fun when we start to calculate our own quantities from ingredients, like IBU, ABV, and SRM. We'll have an entire post dedicated to this, but we created a [fun little visualization tool]({% link _apps/ibu_abv_color.md %}) to explore beer styles in the IBU-ABV-SRM space. This allows you to explore beer styles by where they live in this space.


# 4) What Next?

So where are we going with all this? There's a huge range of different analyses we could do and tools we can create, and this is just the start. We're planning to continue making posts that explore the recipe landscape and answer fun and interesting questions, such as:

* What differentiates a stout and a porter?
* What ingredients define particular styles?
* How do beer styles empirically compare to their BJCP definitions?

Not only this, we'll be making interesting apps that let you do things like:

* Generate a completely AI-based recipe (or AI-assisted if you want to start with a certain set of ingredients)
* Analyze recipes - how does your recipe compare to all of the others in the dataset?
* Hybridize recipe - how do I make a style X - style Y hybrid that retains the most defining characteristics of each style?

But until the next post - happy drinking!
