<%inherit file="local:templates.master"/>
<link rel="stylesheet" type="text/css" media="screen" href="${tg.url('/css/rnms.css')}" />
<div class="row">
<div class="pblock span4">
<h2>Statistics</h2>
%for statrow in statrows:
	<div class="statrow">
	    <label><a href="${statrow[2]}">${statrow[0]}</a></label>
		<span class="field">${statrow[1]}</span>
	</div>
%endfor
</div>
<div class="pblock span6">
<h2>Attribute Status</h2>
${attpie.display() | n }
</div>
</div>


