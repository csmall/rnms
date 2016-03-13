<!DOCTYPE html>
<html lang="en">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    ${self.meta()}
    <title>${self.title()}</title>
    <link rel="stylesheet" type="text/css" media="screen" href="${tg.url('/css/bootstrap.min.css')}" />
    <link rel="stylesheet" type="text/css" media="screen" href="${tg.url('/css/style.css')}" />
    <link rel="stylesheet" type="text/css" media="screen" href="${tg.url('/css/custom.css')}" />
    <link rel="stylesheet" type="text/css" media="screen" href="${tg.url('/css/animate.min.css')}" />
    <link rel="stylesheet" type="text/css" media="screen" href="${tg.url('/css/font-awesome.min.css')}" />
    ${self.head_content()}
</head>
<body class="nav-md">
  <div class="container body">
    <div class="main_container">
      <div class="col-md-3 left_col">
        <div class="left_col scroll-view">
	  <div class="navbar nav_title" style="border: 0;">
	    <a href="${tg.url('/')}" class="site_title"><i class="fa fa-laptop"></i> <span>RNMS</span></a>
	  </div>
	  <div class="clearfix"></div>

	  <div class="profile">
	    <div class="profile_pic">h</div>
	    <div class="profile_info">
%if request.identity:
	      <span>Welcome,</span>
	      <h2>${request.identity['user']}</h2>
%endif
	    </div>
	  </div>
	  <br>
	  ${self.sidebar_menu()}
	</div>
      </div>
      <!-- menu footer buttons -->
      <div class="sidebar-footer hidden-small">
        <a href="${tg.url('/about/')}" data-toggle="tooltip" data-placement="top" title="About RNMS">
          <span class="glyphicon glyphicon-info-sign" aria-hidden="true"></span>
        </a>
        <a href="${tg.url('/admin/')}" data-toggle="tooltip" data-placement="top" title="Settings">
          <span class="glyphicon glyphicon-cog" aria-hidden="true"></span>
        </a>
      </div>
      <!-- /side menu -->
      <!-- top navigation -->
      <div class="top_nav">
        <div class="nav_menu">
	  <nav class="" role="navigation">
	    <div class="nav toggle">
	      <a id="menu_toggle"><i class="fa fa-bars"></i></a>
	    </div>
	    <ul class="nav navbar-nav navbar-right">
	      <li class="">
	        <a href="javascript:;" class="user-profile dropdown-toggle" data-toggle="dropdown" aria-expanded="false">
		  <i class="fa fa-user"></i>
%if request.identity:
	          ${request.identity['user']}
%endif
	 	 <span class="fa fa-angle-down"></span>
	        </a>
	      <ul class="dropdown-menu dropdown-username animated dadeInDown pull-right">
	        <li><a href="javascript:;">  Profile</a></li>
	        <li><a href="javascript:;"><i class="fa fa-sign-out pull-right"></i> Log Out</a></li>
 	      </ul>
	    </ul>
	  </nav>
        </div>
      </div>
      <!-- /top navigation -->
      <!-- page content -->
      <div class="right_col" role="main">
        ${self.content_wrapper()}
      </div>
    </div>
  </div>
  <script src="${tg.url('/javascript/bootstrap.min.js')}"></script>
  <script src="${tg.url('/javascript/custom.js')}"></script>
  <script src="${tg.url('/javascript/jquery.nicescroll.min.js')}"></script>
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
</%def>
<%def name="head_content()"></%def>

<%def name="title()">  </%def>

<%def name="footer()">
  <footer class="footer hidden-xs hidden-sm">
    <p>Copyright &copy; RoseNMS Authors ${h.current_year()}</p>
  </footer>
    <link rel="stylesheet" type="text/css" media="screen" href="${tg.url('/css/rnms.css')}" />
</%def>

<%def name="sidebar_menu()">
<div id="sidebar-menu" class="main_menu_side hidden-print main_menu">
  <div class="menu_section">
    <h3>Overview</h3>
    <ul class="nav side-menu">
      <li><a><i class="fa fa-home"></i> Overview <span class="fa fa-chevron-down"></span></a>
        <ul class="nav child_menu" style="display: none">
	  <li><a href="${tg.url('/')}">Dashboard</a></li>
	  <li><a href="${tg.url('/events')}">Events</a></li>
	</ul>
      </li>
      <li><a><i class="fa fa-cubes"></i> Hosts <span class="fa fa-chevron-down"></span></a>
        <ul class="nav child_menu" style="display: none">
	  <li><a href="${tg.url('/hosts')}">List</a></li>
	  <li><a href="${tg.url('/hosts/map')}">Map</a></li>
	  <li><a href="${tg.url('/hosts/map', {'events':1})}">Map &amp; Events</a></li>
	  <li><a href="${tg.url('/hosts/map',{'alarmed':1})}">Map (Alarmed)</a></li>
	  <li><a href="${tg.url('/hosts/map',{'alarmed':1,'events':1})}">Map &amp; Events (Alarmed)</a></li>
	</ul>
      </li>
      <li><a><i class="fa fa-plug"></i> Attributes <span class="fa fa-chevron-down"></span></a>
        <ul class="nav child_menu" style="display: none">
	  <li><a href="${tg.url('/attributes')}">List</a></li>
	  <li><a href="${tg.url('/attributes/map')}">Map</a></li>
	  <li><a href="${tg.url('/attributes/map', {'events':1})}">Map &amp; Events</a></li>
	  <li><a href="${tg.url('/attributes/map',{'alarmed':1})}">Map (Alarmed)</a></li>
	  <li><a href="${tg.url('/attributes/map',{'alarmed':1,'events':1})}">Map &amp; Events (Alarmed)</a></li>
	</ul>
      </li>
    </ul>
  </div>
  ${self.sidebar_admin()}
</div>
</%def>
<%def name="sidebar_admin()">
  <div class="menu_section">
    <h3>Administration</h3>
    <ul class="nav side-menu">
      <li><a><i class="fa fa-users"></i> Users &amp; Customers <span class="fa fa-chevron-down"></span></a>
        <ul class="nav child_menu" style="display: none">
	  <li><a href="${tg.url('/')}">Customers</a></li>
	  <li><a href="${tg.url('/admin/users')}">Users</a></li>
	  <li><a href="${tg.url('/admin/groups')}">Groups</a></li>
	  <li><a href="${tg.url('/')}">Trigger Users</a></li>
	</ul>
      </li>
      <li><a><i class="fa fa-cubes"></i> Hosts &amp; Attributes <span class="fa fa-chevron-down"></span></a>
        <ul class="nav child_menu" style="display: none">
	  <li><a href="${tg.url('/admin/zones')}">Zones</a></li>
	  <li><a href="${tg.url('/admin/hosts')}">Hosts</a></li>
	  <li><a href="${tg.url('/admin/attributes')}">Attributes</a></li>
	</ul>
      </li>
      <li><a><i class="fa fa-road"></i> Polling <span class="fa fa-chevron-down"></span></a>
        <ul class="nav child_menu" style="display: none">
	  <li><a href="${tg.url('/admin/autodiscoverypolicies')}">A/D Policy</a></li>
	  <li><a href="${tg.url('/admin/attributetypes')}">Attribute Types</a></li>
	  <li><a href="${tg.url('/admin/pollersets')}">Poller Sets</a></li>
	  <li><a href="${tg.url('/admin/pollers')}">Pollers</a></li>
	  <li><a href="${tg.url('/admin/backends')}">Backends</a></li>
	</ul>
      </li>
      <li><a><i class="fa fa-exclamation-triangle"></i> Events<span class="fa fa-chevron-down"></span></a>
        <ul class="nav child_menu" style="display: none">
	  <li><a href="${tg.url('/admin/severitys')}">Severities</a></li>
	  <li><a href="${tg.url('/admin/eventtypes')}">Event Types</a></li>
	  <li><a href="${tg.url('/admin/logfiles')}">Log Files</a></li>
	  <li><a href="${tg.url('/admin/logmatchsets')}">Log Match Sets</a></li>
	</ul>
      </li>
    </ul>
  </div>
</%def>

<%def name="oldmain_menu()">
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
