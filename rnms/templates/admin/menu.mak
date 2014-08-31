<%!
skip_vals = ['SNMPEnterprise']
admin_items = [
  [
    'Users Groups', [
      ['User', '/admin/users/'],
      ['Group', '/admin/groups/'],
      ['Permission', '/admin/permissions/'],
    ],
  ],[
    'Host & Zones', [
      ['Zone', '/admin/zones/'],
      ['Host', '/admin/hosts/'],
      ['Attribute', '/admin/attributes/'],
    ],
  ], [
    'Polling', [
      ['A/D Policy', '/admin/autodiscoverypolicys/'],
      ['Attribute Type', '/admin/attributetypes/'],
      ['Poller Set', '/admin/pollersets/'],
      ['Poller', '/admin/pollers/'],
      ['Backend', '/admin/backends/'],
      ['Graph Type', '/admin/graphtypes/'],
      ['Config Backup', '/admin/configbackupmethods/'],
    ],
  ], [
    'Events', [
      ['Severity', '/admin/severitys/'],
      ['Event Type', '/admin/eventtypes/'],
      ['Log File', '/admin/logfiles/'],
      ['Log Match Set', '/admin/logmatchsets/'],

    ],
  ], [
    'SNMP', [
      ['Community', '/admin/snmpcommunitys/'],
      ['Enterprise', '/admin/snmpenterprises/'],
    ],
  ], [

    'Triggers', [
      ['Trigger', '/admin/triggers/'],
      ['Action', '/admin/actions/'],
    ],
  ],
]
%>
<ul class="nav crud-sidebar hidden-xs hidden-sm">
  % for group_name, group in admin_items:
  <li class="nav-header"><a data-toggle="dropdown" href="#">${group_name}</a>
    <ul class="nav dropdown-menu">
      %for item_name, item_url in group:
      <li class="${('', 'active')[model=='item_name']}"><a href="${tg.url(item_url)}">${item_name}s</a></li>
      %endfor
    </ul>
  </li>
  %endfor
  <li class="nav-header"><a data-toggle="dropdown" href="#">Other</a>
    <ul class="nav dropdown-menu">
      % for lower, item in sorted(tmpl_context.menu_items.items()):
        % if lower not in skip_vals:
        <li class="${item==model and 'active' or ''}">
        <a href="${tmpl_context.crud_helpers.make_link(lower)}">${item}</a>
        </li>
       %endif
      % endfor
    </ul>
  </li>
</ul>
