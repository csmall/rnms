<link rel="stylesheet" type="text/css" href="${w.url('/css/map.css')}" />
<link rel="stylesheet" type="text/css" href="${w.url('/events/mapseveritycss')}" />
%if w.map_groups is None:
	<p><b>No items found</b></p>
%else:
<div class="amap1">
  <div class="amap2">
%for map_group in w.map_groups.values():
	<div class="mapheader">
	  <ul class="maplist">
	    <li rel="mappop" title="${item_data(map_group['group'], map_group['group_fields'])}" data-html="true" data-placement="right">${map_group['group']}</li>
	  </ul>
	</div>
	<div class="mapmain">
	  <ul class="maplist">
%for map_item in map_group['items']:
	<a href="${map_item['url']}"><li rel="mappop" class="mapseverity${map_item['state']}" title="${item_data(map_item['name'], map_item['fields'])}" data-html="true">${map_item['name']}</li></a>

%endfor	
	  </ul>
	</div>
%endfor
  </div>
</div>
%endif
<script type="text/javascript">
$(function(){$('[rel=mappop]').tooltip();});
</script>
<%def name="item_data(title, data)">
<div class='maptip-title'>${title}</div>
%for k,value in data:
	<b>${k}:</b> ${value}</br>
%endfor
</%def>
