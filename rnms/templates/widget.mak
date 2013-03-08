<%inherit file="local:templates.master"/>
	<%def name="title()">
	Widget Test
	</%def>
<div class="row">
<div class="span12">
${widget.display()|n}
</div>
</div>
