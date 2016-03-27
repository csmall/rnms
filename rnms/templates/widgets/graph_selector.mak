  <div class="col-md-4 col-sm-4 col-xs-12">
    <h2>Attribute</h2>
    <div class="form-group">
      <label for="chooseSelection" class="control-label">Selection Type:</label>
      <select id="chooseSelection" class="form-control" name="select_type">
        <option value="">-- Choose Selection Type --</option>
        <option value="host">Host</option>
        <option value="user">User</option>
        <option value="atype">Type</option>
      </select>
      <label id="labelSubSelection" for="chooseSubSelection" class="control-label"></label>
      <select class="form-control" id="chooseSubSelection" disabled="disabled"></select>

      <label for="chooseAttribute" class="control-label">Attributes:</label>
      <select class="form-control" id="chooseAttribute" name="a" disabled="disabled" multiple="multiple"></select>
    </div>
  </div>
  <div class="col-md-4 col-sm-4 col-xs-12">
    <h2>Graph Type</h2>
    <div class="form-group">
      <label for="chooseGraphType" class="control-label">Graphs:</label>
      <select class="form-control" id="chooseGraphType" name="gt" disabled="disabled" multiple="multiple"></select>
      <br />
      <button id="start_graph" type="submit" class="btn btn-success" >Graph</button>
    </div>
  </div>
<script>
$(function() {
  // when the document is ready
%if w.attribute_id is  not None:
$('#chooseAttribute').load(
  "${w.aoption_url}",
  $.param({a:${w.attribute_id}},true),
  function(){$(this).attr('disabled', false);});
%endif
$('#chooseSelection').change(
function(event){
  $('[value=""]',event.target).remove();
  var sel_name = $(this).val();
  if (sel_name == 'host') {
    $('#labelSubSelection').html('Host:');
    $('#chooseSubSelection').load(
      "${w.hoption_url}",
      function(){ $(this).attr('disabled',false).attr('name', 'h');}
      );
      return;
    }
  if (sel_name == 'user') {
    $('#labelSubSelection').html('User:');
    $('#chooseSubSelection').load(
      "${w.coption_url}",
      function(){ $(this).attr('disabled',false).attr('name', 'u');}
      );
      return;
    }
  if (sel_name == 'atype') {
    $('#labelSubSelection').html('Type:');
    $('#chooseSubSelection').load(
      "${w.atoption_url}",
      function(){ $(this).attr('disabled',false).attr('name', 'at');}
      );
      return;
    }
  });
$("#chooseSubSelection").change(
function(event){
  $('#chooseAttribute').load(
    "${w.aoption_url}",
    $(this).serialize(),
    function(){$(this).attr('disabled', false);});
    }
    );
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
    my_id = 'graph-'+$(this).val()+'-'+graphtype_id;
    $("#resulting_graphs").append('<div class="row" id="'+my_id+'"></div>');
    $("#"+my_id).load(
    "${w.graph_url}/"+$(this).val()+"/"+graphtype_id+"?pt="+$("#timeSelection").val());
    });
    });
  });
  
$("#graph_time_span").change(function(event){
  var now = parseInt((new Date).getTime()/1000);
  $(this).attr({'data-start-time':now, 'data-end-time':now-$(this).val()})
  })
});
</script>

