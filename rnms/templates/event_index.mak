<%inherit file="local:templates.master"/>
<link rel="stylesheet" type="text/css" media="screen" href="${tg.url('/events/severitycss')}" />

<%def name="title()">
Rosenberg NMS: Event List
</%def>
<script>
var grid = $("#events-grid-id"), intervalId = setInterval(function(){grid.setGridParam({datatype: 'json'}); grid.trigger('reloadGrid'); }, 4000);
</script>
<div class="row">
  <div class="span12">
    ${w.display() | n}
  </div>
</div>
