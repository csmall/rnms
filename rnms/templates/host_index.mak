<%inherit file="local:templates.master"/>

<%def name="title()">
Rosenberg NMS: Host List
</%def>
    
	<div class="row">
	  <div class="span12">
	    <div class="hosts_table">
		%for host in hosts:
		  <div class="host_row">${host}</div>
		%endfor
		</div>
	  </div>
	</div>
