
<link rel="stylesheet" type="text/css" media="screen" href="${('/css/rnms.css')}" />
<link rel="stylesheet" type="text/css" media="screen" href="${('/events/severitycss')}" />
<span class="table_controls ui-jqgrid-titlebar ui-widget-header ui-corner-top ui-helper-clearfix">
  <span id="span_control">Items: ${str(w.currentPage.items_per_page)} </span>
<span class="pagelist">
hello
% if previous_page in w.currentPage:
    <a class="prevPage" href="/list?page=${w.currentPage}">&lt;&lt;&lt;</a>
% endif
      ${w.currentPage.pager(format='~3~', page_param='page', show_if_single_page=True)}
    <a class="nextPage" href="/list?page=${str(w.currentPage.next_page)}">&gt;&gt;&gt;</a>
</span>
</span>
    <table id="eventtable">
	  <tr id="tableheader">
	    <th>Date</th>
		<th>Type</th>
		<th>Host</th>
		<th>Description</th>
	  </tr>
	  
        %for event in w.events:
        <tr class="severity${str(event.event_type.severity_id)}" onClick="location.href='/events/${str(event.id)}'">
            <td>${str(event.created)}</td>
            <td>${event.event_type.display_name}</td>
			<td><a href="${('/hosts/')}${str(event.host.id)}">${event.host.display_name}</a></td>
			<td>${event.text()}</td>
        </tr>
        %endfor
    </table>

