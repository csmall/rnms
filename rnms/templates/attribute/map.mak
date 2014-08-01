<%inherit file="local:templates.master"/>
%if attribute_map != UNDEFINED:
<div class="row">
  <div class="pblock ui-widget-content ui-corner-bottom span12">
    ${attribute_map.display() | n }
  </div>
</div>
%if eventsgrid is not None:
<div class="row">
  <div class="span12">
    ${eventsgrid.display() | n }
  </div>
</div>
<script type="text/javascript">
var events_grid = $("#events-grid"), intervalID=setInterval(function(){events_grid.setGridParam({datatype:'json'});events_grid.trigger('reloadGrid');},10000);
</script>
%endif
%endif
