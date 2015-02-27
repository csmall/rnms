<!DOCTYPE html>
<html>
<head>
    ${self.meta()}
    <title>${self.title()}</title>
    <link rel="stylesheet" type="text/css" media="screen" href="${tg.url('/css/bootstrap.min.css')}" />
    <link rel="stylesheet" type="text/css" media="screen" href="${tg.url('/css/style.css')}" />
    ${self.head_content()}
</head>
<body class="${self.body_class()}">
    ${self.main_menu()}
  <div class="container fullwidth">
    ${self.content_wrapper()}
  </div>
    ${self.footer()}

  <script src="${tg.url('/javascript/bootstrap.min.js')}"></script>
</body>

<%def name="content_wrapper()">
  <%
    flash=tg.flash_obj.render('flash', use_js=False)
  %>
  % if flash:
      <div class="row">
        <div class="col-md-8 col-md-offset-2">
              ${flash | n}
        </div>
      </div>
  % endif
  ${self.body()}
</%def>

<%def name="body_class()"></%def>
<%def name="meta()">
  <meta charset="${response.charset}" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
</%def>
<%def name="head_content()"></%def>

<%def name="title()">  </%def>

<%def name="footer()">
  <footer class="footer hidden-xs hidden-sm">
    <p>Copyright &copy; RoseNMS Authors ${h.current_year()}</p>
  </footer>
    <link rel="stylesheet" type="text/css" media="screen" href="${tg.url('/css/rnms.css')}" />
</%def>

<%def name="main_menu()">
  <div class="rnms-header">
      <a href="${tg.url('/')}">RoseNMS</a>
    % if tg.auth_stack_enabled:
      <ul class="inav navbar-nav navbar-right">
      % if not request.identity:
        <li><a href="${tg.url('/login')}">Login</a></li>
      % else:
      <li>Logged in as: ${request.identity['repoze.who.userid']} - </li>
        <li><a href="${tg.url('/logout_handler')}">Logout</a></li>
        % if 'manage' in request.identity['permissions']:
        <li><a href="${tg.url('/admin')}">Admin</a></li>
        %endif
      % endif
      </ul>
    % endif
  </div>

  <!-- Navbar -->
  <nav class="ui-widget-header navbar navbar-default">
    <div class="navbar-header">
      <button type="button" class="navbar-toggle" data-toggle="collapse" data-target="#navbar-content">
        <span class="sr-only">Toggle navigation</span>
        <span class="glyphicon-bar"></span>
        <span class="icon-bar"></span>
        <span class="icon-bar"></span>
      </button>
    </div>

    <div class="collapse navbar-collapse" id="navbar-content">
      <ul class="nav navbar-nav">
        % if request.identity:
        <li class="${('', 'active')[page=='index']}"><a href="${tg.url('/')}">Overview</a></li>
          <li class="${('', 'active ')[page=='hosts']}dropdown"><a class="dropdown-toggle" data-toggle="dropdown" href="#" >Hosts<b class="caret"></b></a>
	    <ul class="dropdown-menu" role="menu">
	      <li><a href="${tg.url('/hosts')}">List</a></li>
	      <li><a href="${tg.url('/hosts/map')}">Map</a></li>
	      <li><a href="${tg.url('/hosts/map', {'events':1})}">Map &amp; Events</a></li>
	      <li><a href="${tg.url('/hosts/map',{'alarmed':1})}">Map (Alarmed)</a></li>
	      <li><a href="${tg.url('/hosts/map',{'alarmed':1,'events':1})}">Map &amp; Events (Alarmed)</a></li>
	    </ul>
	  </li>
          <li class="${('', 'active ')[page=='attributes']}dropdown"><a class="dropdown-toggle" data-toggle="dropdown" href="#" >Attributes<b class="caret"></b></a>
	    <ul class="dropdown-menu" role="menu">
	      <li><a href="${tg.url('/attributes')}">List</a></li>
	      <li><a href="${tg.url('/attributes/map')}">Map</a></li>
	      <li><a href="${tg.url('/attributes/map', {'events':1})}">Map &amp; Events</a></li>
	      <li><a href="${tg.url('/attributes/map',{'alarmed':1})}">Map (Alarmed)</a></li>
	      <li><a href="${tg.url('/attributes/map',{'alarmed':1,'events':1})}">Map &amp; Events (Alarmed)</a></li>
	    </ul>
	  </li>
        %if 'manage' in request.identity['permissions']:
        <li class="${('', 'active')[page=='events']}"><a href="${tg.url('/events')}">Events</a></li>
	%endif
        <li class="${('', 'active')[page=='about']}"><a href="${tg.url('/about')}">About</a></li>
        % endif
      </ul>

    </div>
  </nav>
</%def>

</html>
