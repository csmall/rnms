<%inherit file="local:templates.master"/>
<link rel="stylesheet" type="text/css" media="screen" href="${tg.url('/events/severitycss')}" />

<%def name="title()">
Rosenberg NMS: Event List
</%def>
    
	<div class="row">
	  <div class="span12">
	    ${w.display() | n}
	  </div>
	</div>
