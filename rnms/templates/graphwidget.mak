<div>
<div class='rrdgraph'>
  <img src="data:image/png;base64,${w.img_data}" height="${w.img_height}" width="${w.img_width}" />
  <div class="graph_legend">
%for row in w.legend:
	<div class="graph_row_${row[0]}">${row[1]}</div>
%endfor
  </div>
</div>
<div class="rrdgraph_clear"></div>
</div>
