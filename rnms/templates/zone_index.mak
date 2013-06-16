<%inherit file="local:templates.master"/>

<%def name="title()">
Rosenberg NMS: Zone List
</%def>
%if zone_grid != UNDEFINED:
	<div class="row">
	  <div class="span12">
	    ${zone_grid.display() | n}
	  </div>
	</div>
%endif
