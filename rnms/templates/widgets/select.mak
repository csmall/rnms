%if data_name == DEFINED:
<select>
%for ivalue, iname in items:
	<option value="${ivalue}">${iname}</option>
%endfor
</select>
%else:
<select>
%for ivalue, iname, data_val in items:
	<option value="${ivalue}" data-${data_name}="${data_val}">${iname}</option>
%endfor
</select>
%endif
