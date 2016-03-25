<div class="row">
  <div class="col-md-4 col-sm-4 col-xs-12">
    <h2>Attribute</h2>
    <div class="form-group">
      <label for="chooseSelection" class="control-label">Selection Type:</label>
      <select id="chooseSelection" class="form-control" name="select_type">
        <option value="">-- Choose Selection Type --</option>
        <option value="host">Host</option>
      </select>
      <label for="chooseHost" class="control-label">Host:</label>
      <select class="form-control" id="chooseHost" name="h" disabled="disabled"></select>

      <label for="chooseAttribute" class="control-label">Attributes:</label>
      <select class="form-control" id="chooseAttribute" name="a" disabled="disabled" multiple="multiple"></select>
    </div>
  </div>
  <div class="col-md-6 col-sm-6 col-xs-12">
    <h2>Graph Type</h2>
    <div class="form-group">
      <label for="chooseGraphType" class="control-label">Graphs:</label>
      <select class="form-control" id="chooseGraphType" name="gt" disabled="disabled" multiple="multiple"></select>
      <br />
      <button id="start_graph" type="submit" class="btn btn-success" >Graph</button>
    </div>
  </div>
</div>
<script>
$(function() {
  // when the document is ready
%if w.attribute_ids is None:
$('#chooseSelection').change(
function(event){
  $('[value=""]',event.target).remove();
  var sel_name = $(this).val();
  if (sel_name == 'host') {
    $('#chooseHost').load(
      "${w.hoption_url}",
      function(){ $(this).attr('disabled',false);}
      );
    }
  });
$("#chooseHost").change(
function(event){
  $('#chooseAttribute').load(
    "${w.aoption_url}",
    $(this).serialize(),
    function(){$(this).attr('disabled', false);});
    }
    );
%else:
var att_ids = ${w.attribute_ids};
$('#chooseAttribute').load(
  "${w.aoption_url}",
  $.param({a:${w.attribute_ids}},true),
  function(){$(this).attr('disabled', false);});
%endif
$("#chooseAttribute").change(
function(event){
  $('#chooseGraphType').load(
    "${w.gtoption_url}",
    $(this).serialize(),
    function(){$(this).attr('disabled',false);});
    });
$("#start_graph").click(
function(event){
  $("#resulting_graphs").html('');
  $.each($("#chooseGraphType option:selected"),
  function(){
  var graphtype_id=$(this).val();
  $.each($("#chooseAttribute option:selected:[data-atype="+$(this).attr('data-atype')+"]"),
    function(idx, val){
    console.debug('gt: '+graphtype_id+' a:'+$(this).val());
    my_id = 'graph-'+$(this).val()+'-'+graphtype_id;
    $("#resulting_graphs").append('<div class="row" id="'+my_id+'"></div>');
    $("#"+my_id).load(
    "${w.graph_url}/"+$(this).val()+"/"+graphtype_id+"?pt="+$("#graph_time_span").val());
    });
    });
  });
  
$("#graph_time_span").change(function(event){
  var now = parseInt((new Date).getTime()/1000);
  $(this).attr({'data-start-time':now, 'data-end-time':now-$(this).val()})
  })
});
</script>

