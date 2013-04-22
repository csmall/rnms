<%inherit file="local:templates.master"/>
<div class="row">
  <div class="pblock ui-widget-content ui-corner-bottom span12">
    <h2 class="ui-widget-header">Attribute Map</h2>
    ${attribute_map.display() | n }
  </div>
</div>
