<%inherit file="local:templates.master"/>
<%def name="title()">Login Form</%def>
<div class="row">
<div class="span4">
<h2>Welcome to Rosenberg NMS</h2>
<p>
Login to Rosenberg NMS using the form on this page.
</p>
</div>
<div class="span3 offset1 well">
<form action="${tg.url('/login_handler', params=dict(came_from=came_from.encode('utf-8'), __logins=login_counter.encode('utf-8')))}" method="POST">
	<input type="text" id="login" name="login" placeholder="Username"></input><br/>
	<input type="password" id="password" name="password" placeholder="Password"></input>
      	<label class="checkbox" id="labelremember" for="loginremember">remember me
	<input type="checkbox" id="loginremember" name="remember" value="2252000"/>
	</label>
	<input class="btn btn-primary" type="submit" id="submit" value="Login" />
</form>
</div>
</div>
