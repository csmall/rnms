<div id="${w.id}"></div>
<div id="${w.id}_legend" class="legend"></div>
<script>
function setLegend( chart, data ) {
  var legend = $("#${w.id}_legend");
  var colors = chart.data.colors()
  $.each(chart.data.names(), function(key, label) { legend.append('<div class="legend_'+key+'"><i class="fa fa-square" style="color:'+colors[key]+';"></i> '+label+' Max: '+ data['maxs'][key]+' Min: '+ data['mins'][key]+' Last: '+ data['lasts'][key] +'</div>'); });
  return chart;
}
$.getJSON("${w.data_url|n}", function( data ) {
  var ${w.id}Chart = c3.generate({
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
      columns: data['columns'],
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
  setLegend(${w.id}Chart, data);
});
</script>
