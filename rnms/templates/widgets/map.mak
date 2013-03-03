<link rel="stylesheet" type="text/css" href="${tg.url('/css/map.css')}" />
<link rel="stylesheet" type="text/css" href="${tg.url('/events/mapseveritycss')}" />
<div class="amap1">
  <div class="amap2">
%for group_name in att_groups:
	<div class="mapheader">
	  <ul class="maplist">
	    <li>${group_name[0]}</li>
	  </ul>
	</div>
	<div class="mapmain">
	  <ul class="maplist">
%for mapatts in group_name[1]:
		<li class="mapseverity${mapatts[1]}">${mapatts[0]}</li>
%endfor	
	  </ul>
	</div>
%endfor
  </div>
</div>
