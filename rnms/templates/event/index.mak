<%inherit file="local:templates.master"/>
<link rel="stylesheet" type="text/css" media="screen" href="${tg.url('/events/severitycss')}" />

<%def name="title()">
Rosenberg NMS: Event List
</%def>
%if w != UNDEFINED:
<div= class="row">
  <div class="md-xs-12">
    <button id="refresh-button" type="button" class="btn btn-primary btn-lrg active" data-toggle="button">
      <span class="glyphicon glyphicon-refresh"></span> Refresh
    </button>
<div class="row">
  <div class="span12">
    ${w.display(postdata=griddata)| n}
  </div>
</div>
%endif
<script>
var gridUpdateInterval = null;
var grid = $("#events-grid");
function reloadGrid() { grid.setGridParam({datatype: 'json'}).trigger('reloadGrid'); }
function setGridInterval() { gridUpdateInterval = setInterval('reloadGrid()', 10000); }
$(function(){
    setGridInterval();
    datePick = function(elem) { jQuery(elem).datepicker();}
    $("#refresh-button").toggle(
        function(event){clearInterval(gridUpdateInterval);},
        function(event){reloadGrid(); setGridInterval();})
});
</script>
