<%inherit file="local:templates.master"/>
<link rel="stylesheet" type="text/css" media="screen" href="${tg.url('/events/severitycss')}" />
<script src="${tg.url('/javascript/eventrowstyle.js')}"></script>

<%def name="title()">
RoseNMS: Event List
</%def>
<div class="row">
    ${eventtable.display()| n}
</div>
