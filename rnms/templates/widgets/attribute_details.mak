<dl class="dl-horizontal">
  <dt><i class="fa fa-cubes"></i> Host</dt>
  <dd>${w.attribute.host.display_name}</dd>
  <dt><i class="fa fa-tag"></i> Type</dt>
  <dd>${w.attribute.attribute_type.display_name}</dd>
  <dt><i class="fa fa-user"></i> User</dt>
  <dd>${w.attribute.user.display_name}</dd>
  <dt><i class="fa fa-warning"></i> Oper</dt>
  <dd>${w.attribute.oper_state}</dd>
  <dt><i class="fa fa-warning"></i> Admin</dt>
  <dd>${w.attribute.admin_state_name()}</dd>
%for k,v in w.attribute.description_dict().items():
  <dt>${k}</dt>
  <dd>${v}</dd>
%endfor
</dl>
