%if w.fullwidth:
<div class="col-md-12">
%elif w.fillrow:
<div class="col-md-8 col-sm-8 col-xs-12">
%else:
<div class="col-md-4 col-sm-4 col-xs-12">
%endif
%if w.fullheight:
  <div class="x_panel">
%else:
  <div class="x_panel tile fixed_height_320">
%endif
    <div class="x_title">
      <h2>${w.title}</h2>
      <ul class="nav navbar-right panel_toolbox">
        <li><a class="collapse-link"><i class="fa fa-chevron-up"></i></a>
	</li>
	<li><a class="close-link"><i class="fa fa-close"></i></a>
	</li>
      </ul>
      <div class="clearfix"></div>
    </div>
    <div class="x_content">
%for child in w.children:
%if hasattr(child, 'display'):
	${child.display() | n }
%endif
%endfor
    </div>
  </div>
</div>


