<div class="row">
%for child in w.children:
    ${child.display() | n}
%endfor
</div>
