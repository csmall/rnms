<table id="${w.id}"
       data-icon-prefix='fa'
       data-url="${w.data_url}"
       data-toggle="table"
       data-escape="false"
%if w.fit_panel:
       data-height="250"
       data-show-header="false"
       data-show-footer="false"
       data-pagination="false"
       data-show-refesh="false"
%else:
       data-pagination="true"
       data-show-refesh="true"
       data-toolbar="#toolbar"
%endif
       data-side-pagination="server"
       data-sort-name="${w.sort_name}"
%if not w.sort_asc:
       data-sort-order="desc"
%endif
%if w.row_style is not None:
       data-row-style="${w.row_style}"
%endif
%if w.striped:
       data-striped="true"
%endif
       data-classes="table table-hover table-no-bordered"
%if w.filter_params != {}:
       data-query-params="tableparams"
%endif
%if w.enable_search:
       data-search="true"
%endif
%if not w.detail_url and (w.have_checkbox or w.have_radio):
       data-click-to-select="true"
%endif
       >
  <thead><tr>
<%if 'state' in w.row_formatter:
	formatter=' data-formatter=\"'+w.row_formatter['state']+'"'
else:
	formatter=''
%>
%if w.have_checkbox:
    <th data-field="state" data-checkbox="true" ${formatter|n}></th>
%elif w.have_radio:
    <th data-field="state" data-radio="true" ${formatter|n}></th>
%endif
%for col_id, col_title in w.columns:
<%if col_id in w.row_formatter:
	formatter=' data-formatter=\"'+w.row_formatter[col_id]+'"'
else:
	formatter=''
%>
    <th data-field="${col_id}" data-sortable="true"${formatter|n}>${col_title}</th>
%endfor
%for col_id in w.hidden_columns:
    <th data-field="${col_id}" data-visible="false"></th>
%endfor
  </tr>
  </thead>
</table>
%if w.detail_url is not None:
<script>
$('#${w.id}').on('click-row.bs.table', function(e, row, element){ window.location.href='${w.detail_url}'+row['id']; });
</script>
%endif
%if w.filter_params != {}:
<script>
function tableparams(params) {
%for paramkey,paramvalue in w.filter_params.items():
  params['${paramkey}'] = '${paramvalue}';
%endfor
  return params; }
</script>
%endif
