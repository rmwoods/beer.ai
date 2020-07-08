---
permalink: /about/
title: About the project 
---

The compubeer project is maintained by the following people:

<ul> 
{% for member in site.data.members %}
  <li>
    <a href="https://github.com/{{ member.github }}">
      {{ member.name }}
    </a>
  </li>
{% endfor %}
</ul>
