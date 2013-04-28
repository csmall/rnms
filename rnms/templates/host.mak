## Template for details about a specific host
<%inherit file="local:templates.master"/>
<link rel="stylesheet" type="text/css" media="screen" href="${tg.url('/events/severitycss')}" />

<%def name="title()">
% if host is UNDEFINED:
Rosenberg NMS: Undefined Host
% else:
Rosenberg NMS: Host ${host.display_name}
% endif
</%def>

% if host is not UNDEFINED:
<div class="row">
  <div class="span12">
    <div class="page-header">
      <h2>Host ${host.display_name}</h2>
    </div>
  </div>
</div>
<div class="row">
  <div class="span6">
    ${detailsbox.display(text=capture(self.host_details)) | n }
  </div>
  <div class="span4">
    ${attributesbox.display() | n}
  </div>
</div>

<div class="row">
  <div class="span12">
  ${eventsbox.display() | n}
  </div>
</div>

<%def name="host_details()">
    <dl class="dl-horizontal">
      <dt>Zone</dt><dd>${host.zone.display_name}</dd>
      <dt>State</dt><dd>${host_state}</dd>
      <dt>Address</dt><dd>${host.mgmt_address}</dd>
      <dt>Host Type</dt><dd>${vendor} - ${devmodel}</dd>
    </dl>
</%def>
%endif
