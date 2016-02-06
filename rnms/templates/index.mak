<%inherit file="local:templates.master"/>
<%def name="makebox(name, icon, value)">
  <div class="animated flipInY col-md-3 col-sm-4 col-xs-4 tile_stats_count">
    <div class="left"></div>
    <div clas="right">
      <span class="count_top"><i class="fa ${icon}"></i> ${name}</span>
      <div class="count">${value}</div>
    </div>
  </div>
</%def>
<div class="row tile_count">
 ${makebox('Alarms', 'fa-warning', statrows['alarms'])}
 ${makebox('Zones', 'fa-bullseye', statrows['zones'])}
 ${makebox('Hosts', 'fa-cubes', statrows['hosts'])}
 ${makebox('Attributes', 'fa-plug', statrows['attributes'])}
</div>
<div class="row">
  ${eventchart_panel.display()}
</div>
<div class="row">
  ${att_hbar.display() | }
  ${doughnut.display() | }
  ${status_panel.display() | }
</div>
