---
layout: splash-post
title: Welcome To Compubeer
author: everyone
draft: true
#notebook_src: welcome-to-compubeer.html
header:
  image: /assets/images/kettle-feature.jpg
  teaser: /assets/images/kettle-thumbnail.jpg
---

# Outline

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
