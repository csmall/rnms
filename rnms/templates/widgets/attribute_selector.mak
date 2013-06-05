<!DOCTYPE html>
<html>
<head>
<title>Attribute Selector</title>
    <link rel="stylesheet" type="text/css" media="screen" href="${tg.url('/css/bootstrap.min.css')}" />
    <link rel="stylesheet" type="text/css" media="screen" href="${tg.url('/css/bootstrap-responsive.min.css')}" />
    <link rel="stylesheet" type="text/css" media="screen" href="${tg.url('/css/style.css')}" />
    <link rel="stylesheet" type="text/css" media="screen" href="${tg.url('/css/rnms.css')}" />
</head>
<body class="${self.body_class()}">
<script>
$(function() {
    $("#selectable").selectable({
        stop: function() {
            var result = $( "#select-result" ).empty();
            $( ".ui-selected", this).each(function() {
                var index = $( "#selectable li").index(this);
                result.append( " #" + ($index + 1) );
            });
        }
    });
});
</script>
  <div class="container">
      <h1>${w.title}</h1>
      <p>You have selected <span id="select-result">none</span>.</p>
      <ol id="selectable">
%for item in w.items:
        <li>${item}</li>
%endfor
      </ol>
  </div>
</html>
