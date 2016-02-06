## Template for details about a specific attribute
<%inherit file="local:templates.master"/>
<link rel="stylesheet" type="text/css" media="screen" href="${tg.url('/events/severitycss')}" />

<%def name="title()">
%if attribute is UNDEFINED:
RoseNMS: Unknown Attribute
%else:
RoseNMS: ${attribute.host.display_name} -  ${attribute.display_name}
%endif
</%def>
%if attribute is not UNDEFINED:
<div class="row">
  <div class="col-xs-12">
    <div class="page-header">
      <h2>${attribute.host.display_name} -  ${attribute.display_name}</h5>
    </div>
  </div>
</div>
<div class="row">
  ${details_panel.display()}
  ${graph_panel.display()}
</div>
<div class="row">
    Showing
    <select id='graph_choose_graphtype' name='gt' ></select>
for
    <select id="graph_time_span" name="pt">
      <%include file="local:templates.widgets.time_select"/>
    </select>
    <a href="${tg.url('/graphs',{'a':attribute_id})}">
    <button type="button" class="btn btn-primary">
      <span class="glyphicon glyphicon-signal"></span> Graphs
    </button>
    </a>
</div>
<div class="row">
  <div class="col-md-12">
  <div id="resulting_graphs"></div>
  </div>
</div>
<div class="row">
    ${eventsgrid.display(postdata=grid_data) | n}
</div>
%endif
