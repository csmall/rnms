<%inherit file="local:templates.master"/>

<%def name="title()">
RoseNMS: Attribute List
</%def>
<div class="row">
%if attributetable != UNDEFINED:
${attributetable.display() | n}
%endif
</div>
