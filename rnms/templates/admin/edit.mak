<%inherit file="local:templates.master"/>
<%namespace name="menu_items" file="local:templates.admin.menu_items"/>

<%def name="title()">
${tmpl_context.title} - ${model}
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
    <div class="span10">
      <h2>Edit ${model}</h2>
      ${tmpl_context.widget(value=value, action='./') | n}
    </div>
  </div>
  <div style="height:0px; clear:both;"> &nbsp; </div>
