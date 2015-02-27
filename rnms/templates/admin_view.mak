<%inherit file="local:templates.master"/>
<%def name="title()">
RoseNMS Admin:
</%def>
<div class="row">
<%include file="local:templates.admin_menu"/>
  <div class="span10 admin-grid">
  ${tmpl_context.widget(action=mount_point+'.json') |n}
  </div>
</div>
