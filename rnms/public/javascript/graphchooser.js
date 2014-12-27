!function( $ ) {
    $(function() {
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
  });
