<%inherit file="local:templates.master"/>
<link rel="stylesheet" type="text/css" media="screen" href="${tg.url('/css/rnms_graph.css')}" />
<%def name="title()">
Graph
</%def>
<div class="row">
  <div class="span12">
    <div class="page-header">
      <h2>Graph </h2>
    </div>
  </div>
</div>
<select id="graph_time_span" name="pt">
  <option value="">No Preset</option>
  <option value="10">Last 10 Minutes</option>
  <option value="30">Last Half Hour</option>
  <option value="60">Last  Hour</option>
  <option value="720">Last Half Day</option>
  <option value="1440">Last Day</option>
  <option value="10080">Last Week</option>
  <option value="43200">Last Month</option>
</select>
<div id="graphChooserPane">
%if attribute_ids is None:
  <label for="graphChooserControl">Selection Type:</label>
  <select id="graphChooserControl" name="select_type">
    <option value="">-- Choose Selection Type --</option>
    <option value="host">Host</option>
  </select>
  <label for="graph_choose_host">Host:</label>
  <select class="graph_choose_subselect"id="graph_choose_host" name="h" disabled="disabled"></select>
%endif
  <label for="graph_choose_attribute">Attribute:</label>
  <select id="graph_choose_attribute" name="a" disabled="disabled" multiple="multiple"></select>
  <label for="graph_choose_graphtype">Graph Type:</label>
  <select id="graph_choose_graphtype" name="gt" disabled="disabled" multiple="multiple"></select>
  <button id="start_graph" class="btn btn-primary">Graph</button>
</div>
<div id="graph_pane">
  <div id="resulting_graphs"></div>
</div>
<script type="text/javascript">
%if attribute_ids is None:
$('#graphChooserControl').change(
function(event){
  $('[value=""]',event.target).remove();
  var sel_name = $(this).val();
  if (sel_name == 'host') {
    $('#graph_choose_host').load(
      "${tg.url('/hosts/option')}",
      function(){ $(this).attr('disabled',false);}
      );
    }
  })
$("#graphChooserPane .graph_choose_subselect").change(
function(event){
  $('#graph_choose_attribute').load(
    "${tg.url('/attributes/option')}",
    $(this).serialize(),
    function(){$(this).attr('disabled', false);});
    }
    );
%else:
var att_ids = ${attribute_ids};
$('#graph_choose_attribute').load(
  "${tg.url('/attributes/option')}",
  $.param({a:${attribute_ids}},true),
  function(){$(this).attr('disabled', false);});
%endif
$("#graph_choose_attribute").change(
function(event){
  $('#graph_choose_graphtype').load(
    "${tg.url('/graphs/types_option')}",
    $(this).serialize(),
    function(){$(this).attr('disabled',false);});
    });
$("#start_graph").click(
function(event){
  $("#resulting_graphs").html('');
  $.each($("#graph_choose_graphtype option:selected"),
  function(){
  var graphtype_id=$(this).val();
  $.each($("#graph_choose_attribute option:selected:[data-atype="+$(this).attr('data-atype')+"]"),
    function(){
    my_id = 'graph-'+$(this).val()+'-'+graphtype_id
    $("#resulting_graphs").append('<div id="'+my_id+'"></div>');
    $("#"+my_id).load(
    "${tg.url('/graphs/widget/')}"+$(this).val()+"/"+graphtype_id+"?pt="+$("#graph_time_span").val());
    });
    });
  });
  
$("#graph_time_span").change(function(event){
  var now = parseInt((new Date).getTime()/1000);
  $(this).attr({'data-start-time':now, 'data-end-time':now-$(this).val()})
  })
</script>
<div id="target"></div>
