<!DOCTYPE html>
<html lang="en">
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1">

  <title>${tg.config['site_name']} - Login - RNMS </title>
  <link rel="stylesheet" type="text/css" media="screen" href="${tg.url('/css/bootstrap.min.css')}" />
  <link rel="stylesheet" type="text/css" media="screen" href="${tg.url('/css/style.css')}" />
  <link rel="stylesheet" type="text/css" media="screen" href="${tg.url('/css/signin.css')}" />
</head>
<body>
  <div class="container">
    <form class="form-signin" action="${tg.url('/login_handler', params=dict(came_from=came_from, __logins=login_counter))}"
            method="post" accept-charset="UTF-8" class="form-horizontal">
      <h2 class="form-signin">${tg.config['site_name']}</h2>
      <h3 class="form-signin">RNMS Login</h3>
      <label for="loginUsername">Username:</label>
      <input type="text" class="form-control" id="loginUsername" name="login" placeholder="Username" required autofocus/>
      <label for="loginPassword">Password:</label>
      <input type="password" class="form-control" id="loginPassword" name="password" placeholder="Password"/>
      <button type="submit" class="btn btn-lg btn-primary btn-block">Login</button>
   </form>
    <%
      flash=tg.flash_obj.render('flash', use_js=False)
    %>
    % if flash:
      <div class="form-signin">
              ${flash | n}
      </div>
    % endif
</body>
</html>
