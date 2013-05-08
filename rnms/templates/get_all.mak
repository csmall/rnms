<%inherit file="local:templates.master"/>
    <div class="crud_table">
     ${tmpl_context.widget(value=value_list, action=mount_point+'.json', attrs=dict(style="height:200px; border:solid black 3px;")) |n}
    </div>
