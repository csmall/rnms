<%include file="bootstrap_table.mak"/>
<div id="toolbar">
<button class="btn btn-default active" type="button" id="${w.id}-refresh" title="Toggle auto-refresh"><i class="fa fa-refresh icon-refresh"></i></button>
</div>
<script>
var gridUpdateInterval;
function reloadTable() { $("#${w.id}").bootstrapTable('refresh'); }
function setRefreshTable() { gridUpdateInterval = setInterval('reloadTable()', 10000); reloadTable(); }
function clearRefreshTable() { clearInterval(gridUpdateInterval); gridUpdateInterval=null; }
function formatSeverity(value, row, index) { return '<span class="label severity'+row['severity_id']+'">'+value+'</span>';}
$(function(){
    setRefreshTable();
    $("#${w.id}-refresh").on('click', function() { if ($(this).hasClass('active')) { $(this).removeClass('active'); clearRefreshTable(); } else { $(this).addClass('active'); setRefreshTable() } });
});
</script>
