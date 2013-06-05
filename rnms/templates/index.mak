<%inherit file="local:templates.master"/>
<div class="row">
  <div class="span4">
    ${statsbox.display(text=capture(self.statistics)) | n}
  </div>
  <div class="span6">
    ${piebox.display() | n }
  </div>
</div>
<div class="row-fluid"><div class="span6 offset3">
${status_bar.display() | }
</div></div>

<%def name="statistics()">
%for statrow in statrows:
	<div class="statrow">
	    <label><a href="${statrow[2]}">${statrow[0]}</a></label>
		<span class="field">${statrow[1]}</span>
	</div>
%endfor
</%def>
