# -*- coding: utf-8 -*-

"""The base Controller API."""

from tg import TGController, tmpl_context, flash
from tg import request
from tw2.jqplugins.ui import set_ui_theme_name

__all__ = ['BaseController']

VARIABLE_NAMES={
    'a': 'Attribute ID',
    'h': 'Host ID',
    'z': 'Zone ID',
}

class BaseController(TGController):
    """
    Base class for the controllers in the application.

    Your web application should have one of these. The root of
    your application is used to compute URLs used by your app.

    """

    def __call__(self, environ, start_response):
        """Invoke the Controller"""
        # TGController.__call__ dispatches to the Controller method
        # the request is routed to. This routing information is
        # available in environ['pylons.routes_dict']
        set_ui_theme_name('start')

        request.identity = request.environ.get('repoze.who.identity')
        tmpl_context.identity = request.identity
        return TGController.__call__(self, environ, start_response)

    def process_form_errors(self, **kw):
        """ Display errors from a form input """
        msgs=[]
        for val,errmsg in tmpl_context.form_errors.items():
            msgs.append('{} for {}'.format(errmsg, VARIABLE_NAMES.get(val,val)))
        flash(' '.join(msgs), 'error')

