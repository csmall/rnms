<div>
  <canvas id="${w.id}"></canvas>
%if w.show_legend:
  <div id="${w.id}-legend"></div>
%endif
</div>
<script>
$(function () {
$.getJSON("${w.data_url|n}", function( data ) {
    var ${w.id}Chart = new Chart(document.getElementById("${w.id}").getContext("2d")).Line(data, {
    responsive: true,
    scaleSteps: 10,
    maintainAspectRatio: false,
    tooltipFillColor: "rgba(51, 51, 51, 0.55)",
    legendTemplate: "${'<ul class=\\"list-inline <%=name.toLowerCase()%>-legend\\"><% for (var i=0; i<datasets.length; i++){%><li><i class=\\"fa fa-square\\" style=\\"color:<%=datasets[i].strokeColor%>\\"></i> <%if(datasets[i].label){%><%=datasets[i].label%><%}%></li><%}%></ul>'|n}",
    });
%if w.show_legend:
    document.getElementById("${w.id}-legend").innerHTML = ${w.id}Chart.generateLegend();
%endif
});
	});
</script>
