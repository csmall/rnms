<%inherit file="local:templates.master"/>

<%def name="title()">
RoseNMS: Attribute List
</%def>
<div class="row">
${attributetable.display() | n}
</div>
