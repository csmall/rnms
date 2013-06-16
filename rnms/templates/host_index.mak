<%inherit file="local:templates.master"/>

<%def name="title()">
Rosenberg NMS: Host List
</%def>
%if w != UNDEFINED:
	<div class="row">
	  <div class="span12">
	    ${w.display() | n}
	  </div>
	</div>
<script type="text/javascript">
datePick=function(elem){$(elem).datepicker();}
</script>
%endif
