<link rel="stylesheet" type="text/css" href="${w.url('/css/map.css')}" />
<link rel="stylesheet" type="text/css" href="${w.url('/events/mapseveritycss')}" />
<div class="amap1">
  <div class="amap2">
%for map_group in w.map_groups:
	<div class="mapheader">
	  <ul class="maplist">
	    <li>${map_group[0]}</li>
	  </ul>
	</div>
	<div class="mapmain">
	  <ul class="maplist">
%for map_item in map_group[1]:
		<li class="mapseverity${map_item[1]}">${map_item[0]}</li>
%endfor	
	  </ul>
	</div>
%endfor
  </div>
</div>
