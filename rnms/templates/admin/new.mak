<%inherit file="local:templates.master"/>

<%def name="admin_menu()">
<%include file="local:templates.admin.menu"/>
</%def>

<%def name="title()">
${tmpl_context.title} - ${model}
</%def>

  <div class="row">
    <div class="col-md-2">
      % if hasattr(tmpl_context, 'menu_items'):
      ${admin_menu()}
      % endif
    </div>

    <div class="col-md-10">
      <h1 class="page-header">New ${model}</h1>
      ${tmpl_context.widget(value=value, action='./') | n}
    </div>
  </div>
