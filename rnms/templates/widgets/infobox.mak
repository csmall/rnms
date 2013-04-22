<div class="infobox ui-widget-content ui-corner-bottom">
  <h2 class="ui-widget-header">${w.title}</h2>
%if w.text is not None:
    ${w.text | n}
%elif w.child_widget is not None:
${w.child_widget.display() | n}
%endif
</div>
