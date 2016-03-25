<%inherit file="local:templates.master"/>
<%def name="title()">
%if attribute is UNDEFINED:
RoseNMS: Graphs - Unknown Attribute
%else:
RoseNMS: Graphs for ${attribute.host.display_name} -  ${attribute.display_name}
%endif
</%def>
<div class="row">
  <div class="span12">
    <div class="page-header">
      <h2>Graph </h2>
    </div>
  </div>
</div>
<div class="row">
${select_panel.display()|n}
</div>
<select id="graph_time_span" name="pt">
 <%include file="local:templates.widgets.time_select"/>
</select>
<div id="resulting_graphs"></div>
