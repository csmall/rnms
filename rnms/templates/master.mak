<!DOCTYPE html>
<html>
<head>
    ${self.meta()}
    <title>${self.title()}</title>
    <link rel="stylesheet" type="text/css" media="screen" href="${tg.url('/css/bootstrap.min.css')}" />
    <link rel="stylesheet" type="text/css" media="screen" href="${tg.url('/css/bootstrap-responsive.min.css')}" />
    <link rel="stylesheet" type="text/css" media="screen" href="${tg.url('/css/style.css')}" />
    <link rel="stylesheet" type="text/css" media="screen" href="${tg.url('/css/rnms.css')}" />
</head>
<body class="${self.body_class()}">
  <div class="container">
%if main_menu == UNDEFINED:
    ${self.adm_main_menu()}
%else:
    ${main_menu.display(page=page) | n}
%endif
    ${self.content_wrapper()}
    ${self.footer()}
  </div>
<script src="${tg.url('/javascript/bootstrap.min.js')}" type="text/javascript"></script>
</body>

<%def name="content_wrapper()">
  <%
    flash=tg.flash_obj.render('flash', use_js=False)
  %>
  % if flash:
    <div class="row"><div class="span8 offset2">
      ${flash | n}
    </div></div>
  % endif
  ${self.body()}
</%def>

<%def name="body_class()"></%def>
<%def name="meta()">
  <meta charset="${response.charset}" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
</%def>

<%def name="title()">  </%def>

<%def name="footer()">
  <footer class="footer hidden-tablet hidden-phone">
  </footer>
</%def>

<%def name="adm_main_menu()">

  <div class="navbar">
    <div class="navbar-inner">
      <div class="container">
        <div class="brand">Rosenberg NMS</div>
        <ul class="nav nav-pills">
          <li class="${('', 'active')[page=='index']}"><a href="${tg.url('/')}">Overview</a></li>
          <li class="${('', 'active ')[page=='hosts']}dropdown"><a class="dropdown-toggle" data-toggle="dropdown" href="#" >Hosts<b class="caret"></b></a>
	  <ul class="dropdown-menu">
	  <li><a href="${tg.url('/hosts')}">List</a></li>
	  <li><a href="${tg.url('/hosts/map')}">Map</a></li>
	  <li><a href="${tg.url('/hosts/map', {'events':1})}">Map &amp; Events</a></li>
	  <li><a href="${tg.url('/hosts/map',{'alarmed':1})}">Map (Alarmed)</a></li>
	  <li><a href="${tg.url('/hosts/map',{'alarmed':1,'events':1})}">Map &amp; Events (Alarmed)</a></li>
	  </ul>
	  </li>
          <li class="${('', 'active ')[page=='attribute']}dropdown"><a class="dropdown-toggle" data-toggle="dropdown" href="#">Attributes<b class="caret"></b></a>
	  <ul class="dropdown-menu">
	  <li><a href="${tg.url('/attributes')}">List</a></li>
	  <li><a href="${tg.url('/attributes/map')}">Map</a></li>
	  <li><a href="${tg.url('/attributes/map', {'events':1})}">Map &amp; Events</a></li>
	  <li><a href="${tg.url('/attributes/map',{'alarmed':1})}">Map (Alarmed)</a></li>
	  <li><a href="${tg.url('/attributes/map',{'alarmed':1,'events':1})}">Map &amp; Events (Alarmed)</a></li>
	  </ul>
	  </li>
          <li class="${('', 'active')[page=='events']}"><a href="${tg.url('/events')}">Events</a></li>
          <li class="${('', 'active')[page=='about']}"><a href="${tg.url('/about')}">About</a></li>
        </ul>

          <ul class="nav nav-pills pull-right">
            % if not tg.request.identity:
              <li><a href="${tg.url('/login')}">Login</a></li>
            % else:
              <li><a href="${tg.url('/logout_handler')}">Logout</a></li>
              <li><a href="${tg.url('/admin')}">Admin</a></li>
            % endif
          </ul>
      </div>
    </div>
  </div>
</%def>

</html>
