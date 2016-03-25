<div>
<div id="${w.id}"></div>
<div id="${w.id}_legend" class="legend"></div>
</div>
<div class="clearfix"></div>
<script>
$(function() {
  Chart = c3.generate({
    bindto: '#${w.id}',
    legend: {
      hide: true,
    },
%if w.chart_height is not None:
    size: {
       height: ${w.chart_height},
    },
%endif
    data: {
      x: 'x',
      xFormat: '%Y-%m-%d %H:%M',
      columns: ${w.data_columns|n},
%if w.data_groups is not None:
      groups: ${w.data_groups|n},
%endif
%if w.data_colors is not None:
      colors: ${w.data_colors|n},
%endif
%if w.data_types is not None:
      types: ${w.data_types|n},
%endif
      names: ${w.data_names|n},
    },
    axis: {
      x: {
        type: 'timeseries',
      },
      y: {
        tick: {
	  format: d3.format('.3s')
	  }
        }
    }
  });
  var legend = $("#${w.id}_legend");
  var colors = Chart.data.colors()
  $.each(Chart.data.names(), function(key, label) { legend.append('<div class="legend_'+key+'"><i class="fa fa-square" style="color:'+colors[key]+';"></i> '+label+' Max: '+ ${w.maxs|n}[key]+' Min: '+ ${w.mins|n}[key]+' Last: '+ ${w.lasts|n}[key] +'</div>'); });
});
</script>
