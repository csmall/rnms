<%inherit file="local:templates.master"/>
<%def name="title()">
${tmpl_context.title} - ${model} Listing
</%def>
<div class="row">
  <div class="span2">
<%include file="local:templates.admin_menu"/>
  </div>
  <div class="span10">
<%def name="meta()">
<script>
    function crud_search_field_changed(select) {
        var selected = '';
        for (var idx=0; idx != select.options.length; ++idx) {
            if (select.options[idx].selected)
                selected = select.options[idx];
        }
        var field = document.getElementById('crud_search_value');
        field.name = selected.value;
    }
</script>
</%def>
<%def name="body_class()">tundra</%def>
${parent.meta()}
    <h1>${model} Listing</h1>
    <div id="crud_btn_new">
      <a href='${tg.url("new", params=tmpl_context.kept_params)}' class="add_link">New ${model}</a>
      % if search_fields:
        <div id="crud_search">
          <form>
              <select id="crud_search_field" onchange="crud_search_field_changed(this);">
                  % for field, name, selected in search_fields:
                    % if selected is not False:
                      <option value="${field}" selected="selected">${name}</option>
                    % else:
                      <option value="${field}">${name}</option>
                    % endif
                  % endfor
              </select>
              <input id="crud_search_value" name="${current_search[0]}" type="text" placeholder="equals / contains" value="${current_search[1]}" />
              <input type="submit" value="Search"/>
          </form>
        </div>
      % endif
    </div>
    <div class="crud_table">
     ${tmpl_context.widget() |n}
    </div>
  </div>
  <div style="clear:both;"> &nbsp; </div>
</div>
