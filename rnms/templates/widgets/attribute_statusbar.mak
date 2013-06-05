    <div class="ui-widget-content ui-corner-bottom statusbar">
%for sname, scount in w.att_states:
      <div class="status-${sname}">${sname.capitalize()} - ${scount}</div>
%endfor
    </div>
