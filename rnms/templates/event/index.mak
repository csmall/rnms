<%inherit file="local:templates.master"/>
<link rel="stylesheet" type="text/css" media="screen" href="${tg.url('/events/severitycss')}" />

<%def name="title()">
RoseNMS: Event List
</%def>
%if w != UNDEFINED:
<div class="row">
  <div class="span12">
    ${w.display(postdata=griddata)| n}
  </div>
</div>
<script>
var gridUpdateInterval = null;
var grid = $("#events-grid");
function reloadGrid() { grid.setGridParam({datatype: 'json'}).trigger('reloadGrid'); }
function setGridInterval() { gridUpdateInterval = setInterval('reloadGrid()', 10000); }
$(function(){
    setGridInterval();
    $("#t_events-grid").append("${w.toolbar_items|n}");
    datePick = function(elem) { jQuery(elem).datepicker();}
    $("#refresh-button").toggle(
        function(event){$(this).removeClass("btn-success").addClass("btn-danger"); clearInterval(gridUpdateInterval);},
        function(event){$(this).removeClass("btn-danger").addClass("btn-success"); reloadGrid(); setGridInterval();});
    $("#tb-search").click(
        function(event){$("#events-grid").jqGrid('searchGrid');});
});
</script>
%endif
