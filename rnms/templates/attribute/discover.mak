<%inherit file="local:templates.master"/>
<%def name="title()">
RoseNMS: Discovered Attributes
</%def>
%if discover_table != UNDEFINED:
<div class="row">
<button id="add_button" class="btn btn-default">Click</button>
</div>
<div class="row">
${discover_table.display() | n}
</div>
%endif
<script>
$('#add_button').click(function() { var selections=$.each($('#${discover_table.id}').bootstrapTable('getSelections'), function(key, vals){ delete vals['attribute_type']; delete vals['state'];}); window.location = '${add_url}&attribs='+JSON.stringify(selections);});
</script>
