<div class="ui-widget ui-widget-content ui-corner-all" dir="ltr">
  <div class="ui-widget-header ui-corner-top ui-helper-clearfix">
    <a class="HeaderButton" href="javascript:void(0)" role="link" style="right: 0px;">
    <span class="infobox-title">${w.title}</span>
  </div>
%if w.text is not None:
    ${w.text | n}
%elif w.child_widget is not None:
${w.child_widget.display() | n}
%endif
</div>
