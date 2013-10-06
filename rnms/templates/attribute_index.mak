<%inherit file="local:templates.master"/>

<%def name="title()">
Rosenberg NMS: Attribute List
</%def>
%if w != UNDEFINED:
	<div class="row">
	  <div class="span12">
	    ${w.display(postdata=griddata) | n}
	  </div>
	</div>
%endif
