## Template for details about a specific attribute
<%inherit file="local:templates.master"/>

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
  <h2>Details about Attribute: ${attribute.display_name}</h5>
  </div>

  </div>
</div>
%endif

