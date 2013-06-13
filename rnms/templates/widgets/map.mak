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
	    <li rel="mappop" data-original-title="${map_group['group']}" data-content="${item_data(map_group['group_fields'])}">${map_group['group']}</li>
	  </ul>
	</div>
	<div class="mapmain">
	  <ul class="maplist">
%for map_item in map_group['items']:
	<a href="${map_item['url']}"><li rel="mappop" class="mapseverity${map_item['state']}" data-original-title="${map_item['name']}" data-content="${item_data(map_item['fields'])}">${map_item['name']}</li></a>

%endfor	
	  </ul>
	</div>
%endfor
  </div>
</div>
%endif
<script type="text/javascript">
$(function(){$('[rel=mappop]').popover();});
</script>
<%def name="item_data(data)">
%for title,value in data:
	<b>${title}:</b> ${value}</br>
%endfor
</%def>
