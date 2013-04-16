<%inherit file="local:templates.master"/>
	<%def name="title()">
	Widget Test
	</%def>
<div class="row">
<div class="span12">
${w.display()|n}
</div>
</div>
