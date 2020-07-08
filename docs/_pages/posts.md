---
permalink: /posts/ 
---
We will soon be adding posts about our data explorations...

<ul>
  {% for post in site.posts %}
    <li>
      <a href="{{ post.url }}">{{ post.title }}</a>
    </li>
  {% endfor %}
</ul>
