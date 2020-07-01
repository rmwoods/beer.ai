---
permalink: /about/
title: About the project 
---

Compubeer was made by 3 guys with computers who like beer.

# Contributors

<ul> 
{% for member in site.data.members %}
  <li>
    <a href="https://github.com/{{ member.github }}">
      {{ member.name }}
    </a>
  </li>
{% endfor %}
</ul>
