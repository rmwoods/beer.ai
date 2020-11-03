---
layout: splash
permalink: /
header:  
    overlay_image: /assets/images/fermenter_bottoms.jpg
    overlay_filter: 0.5
excerpt: "A data-driven exploration of beer!"
---

<h2>Recent posts</h2>
<div class="grid__wrapper">
  {% for post in site.posts limit:2 %}
    {% include archive-single.html type="grid" %}
  {% endfor %}
</div>
