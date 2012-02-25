<html>
<%inherit file="local:templates.master"/>

<body>
<script type="text/javascript">
var grid = $('#attribute-grid-id');

grid.jqGrid({
  loadComplete: function() {
    alert("two");
	}
	});
</script>
${layoutwidget.display()|n}
</body>

</html>
