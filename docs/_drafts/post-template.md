---
title: My Title
author: coolguy
#notebook_src: welcome-to-compubeer.html
header:
  image: /assets/images/kettle-feature.jpg
  teaser: /assets/images/kettle-thumbnail.jpg
---

Hello, this is a draft. Add your shit here.

If you have other things to include, like an export from a notebook, you can include it like below.

{% if page.notebook_src %}
  {% include {{ page.notebook_src }} %}
{% endif %}
