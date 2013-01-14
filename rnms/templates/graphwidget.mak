<link rel="stylesheet" type="text/css" media="screen" href="${w.tg_url('/css/rnms_graph.css')}" />
<div class='rrdgraph'>
  <div class="graph_title">${w.title}</div>
  <img src="data:image/png;base64,${w.img_data}" height="${w.img_height}" width="${w.img_width}" />
  <div class="graph_legend">
%for row in w.legend:
	<div class="graph_row_${row[0]}">${row[1]}</div>
%endfor
  </div>
</div>
