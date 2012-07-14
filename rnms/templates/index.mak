<%inherit file="local:templates.master"/>

<%def name="title()">
  Welcome to TurboGears 2.1, standing on the shoulders of giants, since 2007
</%def>

${parent.sidebar_top()}

<div id="overall_stats">
  <h2>Rosenberg Statistics</h2>
%for row in rows:
	<div class="stats_row"><span class="stats_label">
	  <a href="${tg.url(row[1])}">${row[0]}</a>:</span> ${row[2]}</div>
%endfor

  
</div>

<%def name="sidebar_bottom()"></%def>
