## Template for details about a specific attribute
<%inherit file="local:templates.master"/>
<link rel="stylesheet" type="text/css" media="screen" href="${tg.url('/events/severitycss')}" />

<%def name="title()">
%if attribute is UNDEFINED:
Rosenberg NMS: Unknown Attribute
%else:
Rosenberg NMS: ${attribute.host.display_name} -  ${attribute.display_name}
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
  <div class="col-xs-12 col-md-6">
    ${detailsbox.display(text=capture(self.attribute_details)) | n }
  </div>
  <div class="col-xs-12 col-md-6">
    <div class="row">
      <div class="col-md-10">
        Showing
        <select id='graph_choose_graphtype' name='gt' ></select>
	for
        <select id="graph_time_span" name="pt">
          <%include file="local:templates.widgets.time_select"/>
        </select>
      </div>
      <div class="col-md-2">
      <a href="${tg.url('/graphs',{'a':attribute_id})}">
	  <button type="button" class="btn btn-primary">
	  <span class="glyphicon glyphicon-signal"></span> Graphs
	  </button>
	</a>
      </div>
    </div>
    <div class="row">
      <div class="col-md-12">
      <div id="resulting_graphs"></div>
      </div>
    </div>
  </div>
</div>
<div class="row">
  <div class="col-xs-12">
    ${eventsgrid.display(postdata=grid_data) | n}
  </div>
</div>

<%def name="attribute_details()">
  <dl class="dl-horizontal">
    <dt>Host</dt><dd><a href="${tg.url('/hosts/{}'.format(attribute.host_id))}">${attribute.host.display_name}</a></dd>
    <dt>Type</dt><dd>${attribute.attribute_type.display_name}</dd>
    <dt>Oper</dt><dd>${attribute.oper_state}</dd>
    <dt>Admin</dt><dd>${attribute.admin_state_name()}</dd>
%for k,v in attribute.description_dict().items():
    <dt>${k}</dt><dd>${v}</dd>
%endfor
  </dl>
</%def>
  </dl>
  </div>
<script>
function load_graph(graph_type_id) {
  $("#resulting_graphs").load(
    "${tg.url('/graphs/widget/')}"+${attribute_id}+"/"+graph_type_id+"?pt="+$("#graph_time_span").val());
}

$(function() {
  $('#btn-change-graph').popover();
  $('#graph_choose_graphtype').load(
    "${tg.url('/graphs/types_option')}",
    $.param({a:${attribute_id}},true),
    function(event){load_graph($(this).val())});
  $('#graph_choose_graphtype option').live('click',function(event){
    load_graph($(this).val());
  });

});
</script>
%endif
<%def name="graph_change_popover()">
</%def>
