---
title: Demo App
author: petra
app_src: ibu_abv_color.html
excerpt: "Chck out my cool app!"
hidden: true
header:
  teaser: http://placekitten.com/200/300
position: 0
---

Remove "Hidden: True" in the front matter to make this visible.

The following is an interactive plot that shows the [IBU](https://en.wikipedia.org/wiki/Beer_measurement#Bitterness) vs the [ABV](https://en.wikipedia.org/wiki/Alcohol_by_volume) of various beer styles in our data set. The color maps approximately to [SRM](https://en.wikipedia.org/wiki/Standard_Reference_Method). The size of the point is proportional to the number of recipes of a given style in our dataset.

{% if page.app_src %}
  {% include {{ page.app_src }} %}
{% endif %}

