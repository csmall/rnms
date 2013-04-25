<%inherit file="local:templates.master"/>
<link rel="stylesheet" type="text/css" media="screen" href="${tg.url('/css/rnms_graph.css')}" />
<div class="row">
  <div class="span12">
  ${selectionbox.display() | n}
  </div>
</div>
%for gw in graph_widgets:
%if loop.even:
<div class="row">
%endif
  <div class="span6">
${gw.display() | n}
  </div>
%if loop.odd or loop.last and loop.even:
</div>
%endif
%endfor
