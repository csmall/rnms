<table class="table table-striped">
  <thead>
    <tr>
      <th>Process</th>
      <th>Status</th>
    </tr>
  </thead>
  <tbody>
%for thread in w.threads:
  <tr>
    <td>${thread['name']}</td>
%if thread['alive']:
    <td><button type="button" class="btn btn-success btn-xs">Alive</button></td>
%else:
    <td><button type="button" class="btn btn-danger btn-xs">Dead</button></td>
%endif
  </tr>
%endfor
  </tbody>
</table>
