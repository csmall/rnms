<%inherit file="local:templates.master"/>
%if host_map != UNDEFINED:
<div class="row">
    ${host_map.display() | n }
</div>
%if events_panel is not None:
<div class="row">
  ${events_panel.display() | n }
</div>
%endif
%endif
