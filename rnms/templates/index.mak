<%inherit file="local:templates.master"/>
<div class="row">
  <div class="span6">
    ${statsbox.display(text=capture(self.statistics)) | n}
  </div>
  <div class="span6">
    ${piebox.display() | n }
  </div>
</div>
<div class="row"><div class="span12">
${status_bar.display() | }
</div></div>

<%def name="statistics()">
<table>
%for statrow in statrows:
	<tr class="statrow">
	 <td><label><a href="${statrow[2]}">${statrow[0]}</a></label></td>
	 <td>${statrow[1]}</td>
	</tr>
%endfor
</table>
</%def>
