<%inherit file="local:templates.master"/>
<%def name="title()">
RoseNMS: Discovered Attributes
</%def>
%if discover_table != UNDEFINED:
<div class="row">
<button id="add_button" class="btn btn-primary" disabled="true">Add Selected Attributes</button>
</div>
<div class="row">
${discover_table.display() | n}
</div>
%endif
<script>
$(function() {
$('#discover_table').on('load-success.bs.table', function(e, data) { $(this).bootstrapTable('updateCell', 1, 'state', {disabled: true});}).
on('check.bs.table', function() { $('#add_button').removeAttr('disabled');}).
on('uncheck.bs.table',function(){ if ($(this).bootstrapTable('getSelections') == '') { $('#add_button').attr('disabled',true);}});
});
$('#add_button').click(function() { var selections=$.each($('#${discover_table.id}').bootstrapTable('getSelections'), function(key, vals){ delete vals['attribute_type']; delete vals['state'];}); $.post('${add_url}', 'h='+${host_id}+'&attribs='+JSON.stringify(selections), function(data, textStatus, jqXHR) { console.debug('yay'); console.debug(data);}) ;});
</script>
