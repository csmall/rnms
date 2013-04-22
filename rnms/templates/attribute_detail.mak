## Template for details about a specific attribute
<%inherit file="local:templates.master"/>
<link rel="stylesheet" type="text/css" media="screen" href="${tg.url('/events/severitycss')}" />

<%def name="title()">
%if attribute is UNDEFINED:
Rosenberg NMS: Unknown Attribute
%else:
Rosenberg NMS: Attribute ${attribute.display_name}
%endif
</%def>
%if attribute is not UNDEFINED:
<div class="row">
  <div class="span12">
    <div class="page-header">
      <h2>Attribute: ${attribute.display_name}</h5>
    </div>
  </div>
</div>
<div class="row">
  <div class="span6">
    ${detailsbox.display(text=capture(self.attribute_details)) | n }
  </div>
</div>
<div class="row">
  <div class="span12">
  ${eventsbox.display() | n}
  </div>
</div>

<%def name="attribute_details()">
  <dl class="dl-horizontal">
    <dt>Host</dt><dd><a href="${tg.url('/hosts/{}'.format(attribute.host_id))}">${attribute.host.display_name}</a></dd>
    <dt>Type</dt><dd>${attribute.attribute_type.display_name}</dd>
    <dt>Oper</dt><dd>${attribute.oper_state_name()}</dd>
    <dt>Admin</dt><dd>${attribute.admin_state_name()}</dd>
%for k,v in attribute.description_dict().items():
    <dt>${k}</dt><dd>${v}</dd>
%endfor
  </dl>
</%def>
  </dl>
  </div>
%endif

