---
title: Other Cool App
author: [aaron, rob, rory]
html: ibu_abv_color.html
---

The following is an interactive plot that shows the [IBU](https://en.wikipedia.org/wiki/Beer_measurement#Bitterness) vs the [ABV](https://en.wikipedia.org/wiki/Alcohol_by_volume) of various beer styles in our data set. The color maps approximately to [SRM](https://en.wikipedia.org/wiki/Standard_Reference_Method). The size of the point is proportional to the number of recipes of a given style in our dataset.

{% if page.ibu-abv-color %}
  {% include {{ page.html }} %}
{% endif %}

