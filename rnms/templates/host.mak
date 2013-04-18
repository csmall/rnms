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

% if host is not DEFINED:
<div class="row">
  <div class="span12">
    <div class="page-header">
      <h2>Host ${host.display_name}</h2>
    </div>
  </div>
</div>
<div class="row">
  <div class="pblock span6">
    <h2>Host Details</h2>
    <dl class="dl-horizontal">
      <dt>Zone</dt><dd>${zone}</dd>
      <dt>Address</dt><dd>${host.mgmt_address | n}</dd>
      <dt>Host Type</dt><dd>${vendor} - ${devmodel}</dd>
    </dl>
  </div>
  <div class="pblock span4">
    <h2>Attribute Status</h2>
    <div>${attw.display() | n}</div>
  </div>
</div>


<div class="row">
  <div class="pblock span12">
  <h2>Events for the host</h2>
  ${events_grid.display() | n}
  </div>
</div>

%endif
