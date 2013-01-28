<div class="attribute_summary">
  <div class="attsum_title">Attributes</div>
  %for i in range(len(w.att_states)):
	<div class="attsum_${i%2 and 'even' or 'odd'}">${w.att_states[i][0]} is ${w.att_states[i][1]}</div>
  %endfor
    <div class="attsum_total">Total ${w.att_total}</div>
</div>
