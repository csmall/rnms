<%doc>
This template can be used for any page that needs a full page PanelTile
and nothing more.  The controller needs to define the content with:
	class MyTile(PanelTile):
	    title = 'My page title'
	    full = True

            class MyText(Text):
	      template = 'rnms.templates.mypage_text'
	
	return dict(page='mypage', page_tile=MyTile())
</%doc>
<%inherit file="local:templates.master"/>
<%
try:
	my_title = page_title
except NameError:
	my_title = ''
%>
<%def name="title()">
%if page_title is not UNDEFINED:
	${page_title}
%endif
</%def>
<div class="row">
${page_tile.display() | n}
</div>
