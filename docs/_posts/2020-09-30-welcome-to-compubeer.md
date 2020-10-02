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

It would be wonderful to have a comprehensive picture of commercially-made beer recipes. Unfortunately that's a a lot harder for a few reasons. Firstly, most professional brewers don't publish their recipes. This makes sense - they're trade secrets. So there is no public website for professional beer recipes. But secondly, it's also the case that there are fewer of them. In 2019 there were [8000+ breweries in the US](https://www.brewersassociation.org/statistics-and-data/national-beer-stats/) and [1100+ in Canada](https://industry.beercanada.com/statistics). This seems like a lot, but on Brewtoad alone there are recipes from **32,000+ brewers**.  Although looking to homebrewers does give a biased view on what a typical beer recipe looks like, it's necessary to get sample that's larger than a few dozen recipes. Also, it turns out this sample is limited than you might think - several professional brewers actually upload their recipes to homebrew sites as well. 

# What does a beer recipe look like in BeerXML?

* What is beerXML
  * Load and print a beerXML file
  * Compare brewtoad and brewersfriend: presence/absense of tags

# 2) Dataset
* How much did we get
  * Count recipes
* How do we represent it? (print dataframe)
  * Comment - can do some basic statistics on this
  * Comment - need to transform this for any sort of ML
* IBU, ABV, OG, FG, etc.
  * Included by some recipes, but we wrote our own functions... more later

# 3) Recipe Landscape
* What does the beer recipe landscape look like
  * \# recipes/styles
  * what's cloned the most often?
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
