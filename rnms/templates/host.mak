## Template for details about a specific host
<%inherit file="local:templates.master"/>

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
		<h2>Details about host ${host.display_name}</h2>
        </div>
      </div>
	  <div class="span8">
	    <dl class="dl-horizontal">
		  <dt>Zone</dt><dd>${zone}</dd>
		  <dt>Management Address</dt><dd>${host.mgmt_address | n}</dd>
		  <dt>Host Type</dt><dd>${vendor} - ${devmodel}</dd>
		</dl>
	  </div>
	  <div class="span4">
	    <div class="well" >
		  <h2>Attribute Status</h2>
		  <div>${attw.display() | n}</div>
		</div>
	  </div>
    </div>
	<div class="row">
	  <div class="span12">
	    Events for the host
	  </div>
	</div>

%endif
