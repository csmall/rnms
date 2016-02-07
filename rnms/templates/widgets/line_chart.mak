<div>
  <canvas id="${w.id}"></canvas>
%if w.show_legend:
  <div id="${w.id}-legend"></div>
%endif
</div>
<script>
        var lineChartData = {
            datasets: [
                {
                    label: "My First dataset",
                    fillColor: "rgba(38, 185, 154, 0.31)", //rgba(220,220,220,0.2)
                    strokeColor: "rgba(38, 185, 154, 0.7)", //rgba(220,220,220,1)
                    pointColor: "rgba(38, 185, 154, 0.7)", //rgba(220,220,220,1)
                    pointStrokeColor: "#fff",
                    pointHighlightFill: "#fff",
                    pointHighlightStroke: "rgba(220,220,220,1)",
                    data: [31, 74, 6, 39, 20, 85, 7]
            },
                {
                    label: "My Second dataset",
                    fillColor: "rgba(3, 88, 106, 0.3)", //rgba(151,187,205,0.2)
                    strokeColor: "rgba(3, 88, 106, 0.70)", //rgba(151,187,205,1)
                    pointColor: "rgba(3, 88, 106, 0.70)", //rgba(151,187,205,1)
                    pointStrokeColor: "#fff",
                    pointHighlightFill: "#fff",
                    pointHighlightStroke: "rgba(151,187,205,1)",
                    data: [82, 23, 66, 9, 99, 4, 2]
            }
        ]

        }

$(document).ready(function () {
$.getJSON("${w.data_url})}", function( data ) {
    var ${w.id}Chart = new Chart(document.getElementById("${w.id}").getContext("2d")).Line(data, {
    responsive: true,
    maintainAspectRatio: false,
    tooltipFillColor: "rgba(51, 51, 51, 0.55)",
    legendTemplate: "${'<ul class=\\"list-inline <%=name.toLowerCase()%>-legend\\"><% for (var i=0; i<datasets.length; i++){%><li><i class=\\"fa fa-square\\" style=\\"color:<%=datasets[i].strokeColor%>\\"></i> <%if(datasets[i].label){%><%=datasets[i].label%><%}%></li><%}%></ul>'|n}",
    });
    document.getElementById("${w.id}-legend").innerHTML = ${w.id}Chart.generateLegend();
});
	});
</script>
