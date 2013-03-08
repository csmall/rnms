<link rel="stylesheet" type="text/css" href="${w.url('/css/map.css')}" />
<link rel="stylesheet" type="text/css" href="${w.url('/events/mapseveritycss')}" />
%if w.map_groups is None:
	<p><b>No items found</b></p>
%else:
<div class="amap1">
  <div class="amap2">
%for map_group in w.map_groups:
	<div class="mapheader">
	  <ul class="maplist">
	    <li rel="mappop" data-original-title="title" data-content="content">${map_group[0]}</li>
	  </ul>
	</div>
	<div class="mapmain">
	  <ul class="maplist">
%for map_item in map_group[1]:
	<a href="${map_item[6]}"><li rel="mappop" class="mapseverity${map_item[1]}" data-original-title="${map_item[0]}" data-content="<b>Host:</b> ${map_item[2]}<br><b>Type:</b> ${map_item[3]}<br><b>Status:</b> ${map_item[4]}<br>${map_item[5]}">${map_item[0]}</li></a>
%endfor	
	  </ul>
	</div>
%endfor
  </div>
</div>
%endif
<script src="${w.url('/javascript/jquery.js')}"></script>
<script src="${w.url('/javascript/bootstrap.min.js')}"></script>
<script>
$('.popover-test').popover()
$('[rel=mappop]').popover()
</script>
