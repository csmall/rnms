## Template for details about a specific host
<%inherit file="local:templates.master"/>
<%def name="title()">
Rosenberg NMS: Discovered Attributes
</%def>
%if w != UNDEFINED:
	<div class="row">
	  <div class="span12">
	    ${w.display() | n}
	  </div>
	</div>
<div class="row">
  <div class="span4">
    <a href="javascript:void(0)" class="btn btn-primary" id="add-rows">Add Selected Rows</a> 
  </div
</div>
<script>
jQuery("#add-rows").click( function() {
   var s;
   s = jQuery("#discovered-atts-grid").jqGrid('getGridParam','selarrrow')
   url = "${edit_url}&" + s
   alert(url);
});
</script>
 %endif

