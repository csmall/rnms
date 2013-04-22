<dl class="dl-horizontal">
  %for att_state in w.att_states:
  <dt class="status-${att_state[0]}">${att_state[0].capitalize()}</dt><dd>${att_state[1]}</dd>
  %endfor
  <dt><a href="${w.url('/attributes/', {'h':w.host_id,})}">Total</a></dt><dd>${w.att_total}</dd>
</dl>
