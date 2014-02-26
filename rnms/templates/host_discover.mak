## Template for details about a specific host
<%inherit file="local:templates.master"/>
<%def name="title()">
Rosenberg NMS: Discovered Attributes
</%def>
%if w != UNDEFINED:
	<div class="row vert-space">
	  <div class="span12">
	    ${w.display(postdata=grid_data) | n}
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
   s = $("#discovered-atts-grid").jqGrid('getGridParam','selarrrow')
   url = "${edit_url}&" + s
   alert(url);
});
</script>
 %endif

