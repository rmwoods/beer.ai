---
layout: splash-post
title: Our Dataset
author: everyone
read_time: false
draft: false
#notebook_src: welcome-to-compubeer.html
header:
  image: /assets/images/bells_kettle.png
  teaser: /assets/images/bells_kettle.png
---

How do you teach your computer about beer?

Ideally, you'd pour it one. But as much as a CD tray looks like a coaster, that doesn't usually go well. In fact, without a few hundred thousand dollars of [equipment](https://en.wikipedia.org/wiki/Gas_chromatography), even giving your laptop an idea of what that beer tastes like is tricky. 

But you can tell your computer how that beer is made. There's a file format for that: [BeerXML](http://beerxml.com/). And with enough of these files, representing a large enough number of beers, we can use data science tools to teach computers and ourselves about beer. 

Compubeer is a project to do just that, between 4 people who like computers, numbers and beer. This first post is about the starting point for these explorations: a discussion about a beer recipe dataset. We've assembled 400,000 homebrew beer recipes. We'll show you what that looks like, and what those recipes can tell us at a first glance.

# Outline
* What a BeerXML file looks like
* How we assembled them into a dataset
* What the dataset tells us about beer style

# Old

* What we want to know about beer
* What beer data is out there
* What is beerXML
  * Load and print a beerXML file
  * Compare brewtoad and brewersfriend: presence/absense of tags
* How much did we get
  * Count recipes
* How did we represent it
  * Print a DataFrame  
* What does the beer recipe landscape look like
  * \# recipes/styles
  * what's cloned the most often?
  * most common malt, hop, yeast names
  * batch sizes
* Sneak preview: beer measurables (IBU, ABV, SRM)

# What is Compubeer?

* What is this site?
* What we want to know about beer

# Our Dataset

* What beer data is out there?

# Beer.xml content

* What is a beer XML?
  * What one looks like
  * Brewtoad vs Brewersfriend content
* How much did we get?

# Our representation

* How do we represent it? (print dataframe)
  * Comment - can do some basic statistics on this
  * Comment - need to transform this for any sort of ML
* IBU, ABV, OG, FG, etc.
  * Included by some recipes, but we wrote our own functions... more later


# Recipe Landscape

* \# recipes/styles
* what's cloned the most often?
* most common malt, hop, yeast names
* batch sizes

# What Next?

Roadmap:
* Recipe analysis
* Recipe generation
* ...

As a sneak Peak: IBU, ABV, SRM...

{% if page.notebook_src %}
  {% include {{ page.notebook_src }} %}
{% endif %}
