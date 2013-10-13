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
        <li class="nav-header">Polling</li>
        <li class="${('', 'active')[model=='AttributeType']}"><a href="${tg.url('/admin/attributetypes/')}">Attribute Types</a></li>
        <li class="${('', 'active')[model=='PollerSet']}"><a href="${tg.url('/admin/pollersets/')}">Poller Sets</a></li>
        <li class="${('', 'active')[model=='Poller']}"><a href="${tg.url('/admin/pollers/')}">Pollers</a></li>
        <li class="${('', 'active')[model=='Backend']}"><a href="${tg.url('/admin/backends/')}">Backends</a></li>
        <li class="${('', 'active')[model=='AutodiscoveryPolicy']}"><a href="${tg.url('/admin/autodiscoverypolicys/')}">Discovery Policy</a></li>
      </ul>
    </div>
    <div class="well" style="padding: 8px 0;">
      <ul class="nav nav-list">
        <li class="nav-header">Events</li>
        <li class="${('', 'active')[model=='EventType']}"><a href="${tg.url('/admin/eventtypes/')}">Event Types</a></li>
        <li class="${('', 'active')[model=='EventSeverity']}"><a href="${tg.url('/admin/severitys/')}">Severities</a></li>
        <li class="${('', 'active')[model=='EventState']}"><a href="${tg.url('/admin/eventstates/')}">States</a></li>
        <li class="${('', 'active')[model=='LogFile']}"><a href="${tg.url('/admin/logfiles/')}">Log Files</a></li>
        <li class="${('', 'active')[model=='LogMatchSet']}"><a href="${tg.url('/admin/logmatchsets/')}">Match Sets</a></li>
      </ul>
    </div>
