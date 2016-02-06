## Template for details about a specific host
<%inherit file="local:templates.master"/>
<link rel="stylesheet" type="text/css" media="screen" href="${tg.url('/events/severitycss')}" />

<%def name="title()">
% if host is UNDEFINED:
RoseNMS: Undefined Host
% else:
RoseNMS: Host ${host.display_name}
% endif
</%def>

<div class="page-title">
  <div class="title_left">
% if host is UNDEFINED:
    <h3>Undefined Host</h3>
  </div>
</div>
%else:
    <h3>Host ${host.display_name} Details</h3>
  </div>
</div>
<div class="clearfix"></div>
<div class="row">
${details_panel.display()}
${attributes_panel.display() | }
${status_panel.display() | }
</div>
<div class="row">
  ${events_panel.display() | n}
</div>
%endif
