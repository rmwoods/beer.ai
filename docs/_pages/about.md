---
permalink: /about/
title: About 
---

Compubeer is a data-driven exploration of beer and brewing. We use data science tools to tap the collective knowledge of brewers.  

Contributors:
<ul> 
{% for member in site.data.members %}
  <li>
    <a href="https://github.com/{{ member.github }}">
      {{ member.name }}
    </a>
  </li>
{% endfor %}
</ul>
