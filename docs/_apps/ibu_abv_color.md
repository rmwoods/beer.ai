---
title: Style Landscape
author: rory
app_src: ibu_abv_color.html
excerpt: "Where does each beer style live in the world of IBU, ABV and SRM?"
header:
  teaser: assets/images/ibu_abv_color.png
position: 1
---

The world of beer is a big place. Beer can be gentle or bitter, watery or boozy, gold or ruby or brown or dark, or a tangle of places in between. When we try a new style of beer, how are we supposed know where it lives? Taking measurements helps sort through the wilderness. There are three numbers in particular that brewers and drinkers use to navigate beer style:

* [IBU](https://en.wikipedia.org/wiki/Beer_measurement#Bitterness), a measure of bitterness
* [ABV](https://en.wikipedia.org/wiki/Alcohol_by_volume), a measure of booziness
* [SRM](https://en.wikipedia.org/wiki/Standard_Reference_Method), a measure of colour


This plot shows where each style lives in the parameter space of IBU, ABV and SRM. 

*These results come from our dataset of 400,000 beer recipes.* 
*The size of each point is proportional to how many recipes available for each style: larger circles are very common styles, smaller circles are rare.* 

{% if page.app_src %}
  {% include {{ page.app_src }} %}
{% endif %}

