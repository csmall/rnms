<!DOCTYPE html>
<html>
<head>
</head>
<body>
%if errmsg != UNDEFINED:
	${errmsg}
%endif
%if w != UNDEFINED:
${w.display() |n}
%endif
<script type="text/javascript">
var siUnits = { 'G':1000000000, 'M':1000000, 'k':1000, '':1, 'm': 0.001};
tickFormatter=function(format, val){
  $.each(siUnits, function(unit_name, divisor){
  if (val >= divisor) {
    val = val / divisor;
    val = val.toFixed(1)+unit_name;
    return false;
    }
  });
  return val;
}
 </script> 
</body>
</html>
