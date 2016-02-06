<h4>${w.title}</h4>
%for data_row in w.graph_data:
<div class="widget_summary">
  <div class="w_left w_25">
    <span>${data_row[0]}</span>
  </div>
  <div class="w_center w_55">
    <div class="progress">
      <div class="progress-bar bg-green" role="progressbar" aria-valuenow="60" aria-valuemin="0" aria-valuemax="100" style="width: ${data_row[1]}%;">
        <span class="sr-only">60% Complete</span>
      </div>
    </div>
  </div>
  <div class="w_right w_20">
    <span>${data_row[2]}</span>
  </div>
  <div class="clearfix"></div>
</div>
%endfor


