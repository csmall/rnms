<div class="" role="tabpanel">
  <ul id="${w.id}" class="nav nav-tabs bars_tabs" role="tablist">
%for idx, tab in enumerate(w.tabs):
    <li role="presentation" class="${'active' if idx == 1 else ''}">
      <a href="#${w.id}_content${idx}" id="${tab[0]}" role="tab" data-toggle="tab" aria-expanded="${'true' if idx == 1 else 'false'}">${tab[1]}</a>
    </li>
%endfor
  </ul>
  <div id="${w.id}Content" class="tab-content">
%for idx, child in enumerate(w.children):
    <div role="tabpanel" class="tab-pane fade active in" id="${w.id}_content${idx}" aria-labelledby="${w.tabs[idx][0]}">
      ${child.display() | n}
    </div>
%endfor
  </div>
</div>

