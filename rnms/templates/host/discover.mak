<%inherit file="local:templates.master"/>
<%def name="title()">
RoseNMS: Discovered Attributes
</%def>
${discover_table.display() | n}
