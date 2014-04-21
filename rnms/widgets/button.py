
from markupsafe import Markup


def Button(url, icon, btn_type='primary', tooltip=''):
    """ Return some markup for this button"""
    if tooltip != '':
        tooltip = ' title="{}'.format(tooltip)
    return Markup('''
<a href="{}" class="btn btn-{}"{}>
    <span class="glyphicon glyphicon-{}"></span>
</a>
'''.format(url, btn_type, tooltip, icon))
