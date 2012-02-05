<%inherit file="local:templates.master"/>

<%def name="title()">
  ${item_type} ${item_id} details
</%def>

${parent.sidebar_top()}

<h2>Details for ${item_type} ${item_id}</h2>

<table class="item_detail">
%for key,value in attribs:
<tr><td class="detail_key">${key}</td><td class="detail_value">${value}</td></tr>
%endfor
</table>

<%def name="sidebar_bottom()"></%def>
