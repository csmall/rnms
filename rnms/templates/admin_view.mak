<%inherit file="local:templates.master"/>
<%def name="title()">
Rosenberg NMS Admin:
</%def>
<div class="row">
  <div class="span2">
  <div class="well" style="padding: 8px 0;">
     <ul class="nav nav-list">
     <li class="nav-header">Users &amp; Groups</li>
     <li class="${('', 'active')[model=='User']}"><a href="${tg.url('/admin/users/')}">Users</a></li>
     <li class="${('', 'active')[model=='Group']}"><a href="${tg.url('/admin/groups/')}">Groups</a></li>
     <li class="${('', 'active')[model=='Permission']}"><a href="${tg.url('/admin/permissions/')}">Permissions</a></li>
     <li class="nav-header">Host &amp; Zones</li>
     <li class="${('', 'active')[model=='Zone']}"><a href="${tg.url('/admin/zones/')}">Zones</a></li>
     <li class="${('', 'active')[model=='Host']}"><a href="${tg.url('/admin/hosts/')}">Hosts</a></li>
     <li class="${('', 'active')[model=='Attribute']}"><a href="${tg.url('/admin/attributes/')}">Attributes</a></li>
     </ul>
     </div>
     <h3>Administration</h3>
  <div class="well" style="padding: 8px 0;">
     <ul class="nav nav-list">
     <li class="nav-header">Events</li>
     <li class="${('', 'active')[model=='EventType']}"><a href="${tg.url('/admin/eventtypes/')}">Event Types</a></li>
     <li class="${('', 'active')[model=='EventSeverity']}"><a href="${tg.url('/admin/eventseverities/')}">Severities</a></li>
     <li class="${('', 'active')[model=='EventState']}"><a href="${tg.url('/admin/eventstates/')}">States</a></li>
     </ul>
  </div>
  </div>
  <div class="span10 admin-grid">
  ${tmpl_context.widget(value=value_list, action=mount_point+'.json', params=tmpl_context.kept_params, attrs=dict(style="height:200px; border:solid black 3px;")) |n}
  </div>
</div>
