<%namespace name="tw" module="tw2.core.mako_util"/>

<span class="table_controls">
  <span id="span_control">Items: ${w.currentPage.items_per_page} </span>
<span class="pagelist">
    <a class="prevPage" href="/list?page=${w.currentPage.previous_page}">&lt;&lt;&lt;</a>
      ${w.currentPage.pager(format='~3~', page_param='page', show_if_single_page=True)}
    <a class="nextPage" href="/list?page=${w.currentPage.next_page}">&gt;&gt;&gt;</a>
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
        <tr class="severity${event.event_type.severity_id}" onClick="location.href='${tg.url('/events/')}${event.id}'">
            <td>${event.created}</td>
            <td>${event.event_type.display_name}</td>
			<td><a href="${tg.url('/hosts/')}${event.host.id}">${event.host.display_name}</a></td>
			<td>${event.text()}</td>
        </tr>
        %endfor
    </table>

