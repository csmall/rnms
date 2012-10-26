<%inherit file="local:templates.master"/>
<link rel="stylesheet" type="text/css" media="screen" href="${tg.url('/css/rnms.css')}" />
<link rel="stylesheet" type="text/css" media="screen" href="${tg.url('/events/severitycss')}" />

<%def name="title()">
  Welcome to TurboGears 2.1, standing on the shoulders of giants, since 2007
</%def>


<h2>Content Type Dispatch</h2>
<p>
This page shows how you can provide multiple pages
directly from the same controller method.  This page is generated 
from the expose decorator with the template defintion provided.
You can provide a url with parameters and this page will display
the parameters as html, and the json version will express
the entries as JSON.  Here, try it out: <a href="/data.html?a=1&b=2">/data.html?a=1&b=2</a>
</p>

<p>Click here for the <a href="${tg.url('/data.json', params=params)}">JSON Version of this page.</a></p>

<span class="table_controls">
  <span id="span_control">Items: ${currentPage.items_per_page} </span>
<span class="pagelist">
    <a class="prevPage" href="/list?page=${currentPage.previous_page}">&lt;&lt;&lt;</a>
      ${currentPage.pager(format='~3~', page_param='page', show_if_single_page=True)}
    <a class="nextPage" href="/list?page=${currentPage.next_page}">&gt;&gt;&gt;</a>
</span>
</span>

    <table id="eventtable">
	  <tr id="tableheader">
	    <th>Date</th>
		<th>Type</th>
		<th>Host</th>
		<th>Description</th>
	  </tr>
	  
        %for event in events:
		${event}
        #<tr class="severity${event.event_type.severity_id}" onClick="location.href='${tg.url('/events/')}${event.id}'">
        #    <td>${event.created}</td>
        #    <td>${event.event_type.display_name}</td>
		#	<td><a href="${tg.url('/hosts/')}${event.host.id}">${event.host.display_name}</a></td>
		#	<td>${event.text()}</td>
        #</tr>
        %endfor
    </table>


