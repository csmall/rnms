<%inherit file="local:templates.master"/>
<link rel="stylesheet" type="text/css" media="screen" href="${tg.url('/events/severitycss')}" />

<%def name="title()">
Rosenberg NMS: Event List
</%def>
%if w != UNDEFINED:
<div class="row">
  <div class="span12">
    ${w.display(postdata=griddata) | n}
  </div>
</div>
%endif
<script>
var grid = $("#events-grid");
var intervalId = setInterval(function(){grid.setGridParam({datatype: 'json'}); grid.trigger('reloadGrid'); }, 10000);
datePick = function(elem) { jQuery(elem).datepicker();}
</script>
