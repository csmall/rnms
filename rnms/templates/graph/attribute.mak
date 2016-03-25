<%inherit file="local:templates.master"/>
<%def name="title()">
%if attribute is UNDEFINED:
RoseNMS: Graphs - Unknown Attribute
%else:
RoseNMS: Graphs for ${attribute.host.display_name} -  ${attribute.display_name}
%endif
</%def>
%if attribute is not UNDEFINED:
<div class="row">
  <div class="col-xs-12">
    <div class="page-header">
      <h2>Graphs for ${attribute.host.display_name} -  ${attribute.display_name}</h2>
    </div>
  </div>
</div>
<div class="row">
  ${select_panel.display()}
</div>
<div id="rnms_graphs">
</div>
%endif
