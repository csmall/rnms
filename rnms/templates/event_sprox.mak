<%inherit file="local:templates.master"/>

<%def name="title()">
  Welcome to TurboGears 2.1, standing on the shoulders of giants, since 2007
</%def>

${parent.sidebar_top()}

${tmpl_context.widget(value=value) | n}

<%def name="sidebar_bottom()"></%def>
