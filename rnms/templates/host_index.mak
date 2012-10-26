<%inherit file="local:templates.master"/>

<%def name="title()">
  Welcome to TurboGears 2.1, standing on the shoulders of giants, since 2007
</%def>

<div class="map" width="${itemmap['width']}">
<%
   x=0
   y=10
%>
%for item in items:
	<div class="map_item" id="11" style="position: absolute; top: ${y}px; left: ${x}px">
	<div class="map_item_title">${item['title']}</div>
	</div>
	<%
x += 100
if x > itemmap['width']:
	x = 0
	y += 100
	%>
%endfor
</div>

