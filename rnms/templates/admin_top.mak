<%inherit file="local:templates.master"/>
<%namespace name="menu_items" file="local:templates.admin.menu_items"/>

<%def name="title()">
Rosenberg NMS Admin:
</%def>
<%def name="body_class()">tundra</%def>
<%def name="meta()">
  ${menu_items.menu_style()}
  ${parent.meta()}
</%def>
  <div class="row">
    <div class="span2">
    ${menu_items.menu_items()}
    </div>
    <div class="span8 hidden-phone hidden-tablet">
      <div class="well">
        <h1>Rosenberg Administration</h1>
	<p>Choose from the left set of menus the items you want to edit, delete
	or change.
	</p>
      </div>
    </div>
  </div>
  <div style="height:0px; clear:both;"> &nbsp; </div>
