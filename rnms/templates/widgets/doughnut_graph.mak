<table class="" style="width:100%">
  <tr>
    <th style="width:37%;">
      <p>${w.graph_title}</p>
    </th>
    <th>
      <div class="col-lg-7 col-md-7 col-sm-7 col-xs-7">
        <p class="">${w.label_title}</p>
      </div>
      <div class="col-lg-5 col-md-5 col-sm-5 col-xs-5">
        <p class="">${w.value_title}</p>
      </div>
    </th>
  </tr>
  <tr>
    <td>
      <canvas id="${w.id}" height="140" width="140" style="margin: 15px 10px 10px 0"></canvas>
    </td>
    <td>
      <table class="tile_info">
%for i,row in enumerate(w.graph_data):
        <tr>
          <td>
	  <p><i class="fa fa-square" style="color:${w.graph_colors[i%len(w.graph_colors)]};"></i>${row[0]}</p>
	  </td>
	  <td>${row[1]}</td>
        </tr>
%endfor
      </table>
    </td>
  </tr>
</table>
<script>
  var doughnutData = [
%for i,field in enumerate(w.graph_data):
    {
      value: ${field[1]},
color: "${w.graph_colors[i%len(w.graph_colors)]}"
    },
%endfor
    ];
  var my${w.id} = new Chart(document.getElementById("${w.id}").getContext("2d")).Doughnut(doughnutData);
</script>

