<%inherit file="local:templates.master"/>

<%def name="title()">
RoseNMS: Zone List
</%def>
%if zone_panel != UNDEFINED:
<div class="row">
   ${zone_panel.display() | n}
</div>
%endif
