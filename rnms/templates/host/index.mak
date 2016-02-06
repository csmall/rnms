<%inherit file="local:templates.master"/>

<%def name="title()">
RoseNMS: Host List
</%def>
${hosttable.display() | n}
