  <div class="navbar">
    <div class="navbar-inner">
      <div class="container">
        <div class="brand">Rosenberg NMS</div>
        <ul class="nav nav-pills">
          <li class="${('', 'active')[w.page=='index']}"><a href="${w.tg.url('/')}">Overview</a></li>
%if w.permissions['host']:
          <li class="${('', 'active ')[w.page=='hosts']}dropdown"><a class="dropdown-toggle" data-toggle="dropdown" href="#" >Hosts<b class="caret"></b></a>
	  <ul class="dropdown-menu">
	  <li><a href="${w.tg.url('/hosts')}">List</a></li>
	  <li><a href="${w.tg.url('/hosts/map')}">Map</a></li>
	  <li><a href="${w.tg.url('/hosts/map', {'events':1})}">Map &amp; Events</a></li>
	  <li><a href="${w.tg.url('/hosts/map',{'alarmed':1})}">Map (Alarmed)</a></li>
	  <li><a href="${w.tg.url('/hosts/map',{'alarmed':1,'events':1})}">Map &amp; Events (Alarmed)</a></li>
	  </ul>
	  </li>
          <li class="${('', 'active ')[w.page=='attribute']}dropdown"><a class="dropdown-toggle" data-toggle="dropdown" href="#">Attributes<b class="caret"></b></a>
	  <ul class="dropdown-menu">
	  <li><a href="${w.tg.url('/attributes')}">List</a></li>
	  <li><a href="${w.tg.url('/attributes/map')}">Map</a></li>
	  <li><a href="${w.tg.url('/attributes/map', {'events':1})}">Map &amp; Events</a></li>
	  <li><a href="${w.tg.url('/attributes/map',{'alarmed':1})}">Map (Alarmed)</a></li>
	  <li><a href="${w.tg.url('/attributes/map',{'alarmed':1,'events':1})}">Map &amp; Events (Alarmed)</a></li>
	  </ul>
	  </li>
%endif
%if w.permissions['manage']:
          <li class="${('', 'active')[w.page=='events']}"><a href="${w.tg.url('/events')}">Events</a></li>
%endif
          <li class="${('', 'active')[w.page=='about']}"><a href="${w.tg.url('/about')}">About</a></li>
        </ul>

          <ul class="nav nav-pills pull-right">
            % if not w.logged_in:
              <li><a href="${w.tg.url('/login')}">Login</a></li>
            % else:
              <li><a href="${w.tg.url('/logout_handler')}">Logout</a></li>
%if w.permissions['manage']:
              <li><a href="${w.tg.url('/admin')}">Admin</a></li>
%endif
            % endif
          </ul>
      </div>
    </div>
  </div>
