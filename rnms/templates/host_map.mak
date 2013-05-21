<%inherit file="local:templates.master"/>
%if host_map != UNDEFINED:
<div class="row">
  <div class="pblock ui-widget-content ui-corner-bottom span12">
    <h2 class="ui-widget-header">Host Map</h2>
    ${host_map.display() | n }
  </div>
</div>
%if eventsbox is not None:
<div class="row">
  <div class="span12">
    ${eventsbox.display() | n }
  </div>
</div>
%endif
%endif
