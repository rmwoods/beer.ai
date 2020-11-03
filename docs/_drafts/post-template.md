---
title: Post template
author: coolguy
read_time: false
#notebook_src: welcome-to-compubeer.html
header:
  image: /assets/images/kettle-feature.jpg
  teaser: /assets/images/kettle-thumbnail.jpg
---

This is a sample post.

If you have other things to include, like an export from a notebook, you can include it like below.

{% if page.notebook_src %}
  {% include {{ page.notebook_src }} %}
{% endif %}
