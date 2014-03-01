<%inherit file="local:templates.master"/>
%if host_map != UNDEFINED:
<div class="row">
  <div class="span12">
    ${host_map.display() | n }
  </div>
</div>
%if events_grid is not None:
<div class="row">
  <div class="span12">
    ${events_grid.display() | n }
  </div>
</div>
%endif
%endif
