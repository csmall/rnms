<%inherit file="local:templates.master"/>
%if attribute_map != UNDEFINED:
<div class="row">
  <div class="pblock ui-widget-content ui-corner-bottom span12">
    ${attribute_map.display() | n }
  </div>
</div>
%if events_panel is not None:
<div class="row">
  ${events_panel.display() | n }
</div>
%endif
%endif
