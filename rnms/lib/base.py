# -*- coding: utf-8 -*-

"""The base Controller API."""
from tg import TGController, tmpl_context
#from tg.render import render
from tg import request
#from tg.i18n import ugettext as _, ungettext

#import rnms.model as model
from tw2.jqplugins.ui import set_ui_theme_name

# Rnms specific imports
from formencode import validators, Invalid
from tg import flash
from rnms.model import DBSession

__all__ = ['BaseController', 'BaseGridController']

VARIABLE_NAMES = {
    'a': 'Attribute ID',
    'h': 'Host ID',
    'z': 'Zone ID',
}

# Common griddata parameters
GRID_VALIDATORS = {
    'page': validators.Int(min=1),
    'rows': validators.Int(min=1),
    'sidx': validators.String(),
    'sord': validators.String(),
    '_search': validators.StringBool(),
    'searchOper': validators.String(),
    'searchField': validators.String(),
    'searchString': validators.String(),
}


class BaseController(TGController):
    """
    Base class for the controllers in the application.

    Your web application should have one of these. The root of
    your application is used to compute URLs used by your app.

    """

    def __call__(self, environ, context):
        """Invoke the Controller"""
        # TGController.__call__ dispatches to the Controller method
        # the request is routed to.
        set_ui_theme_name('hot-sneaks')

        request.identity = request.environ.get('repoze.who.identity')
        tmpl_context.identity = request.identity
        return TGController.__call__(self, environ, context)

    def process_form_errors(self, **kw):
        """ Display errors from a form input """
        msgs = []
        for val, errmsg in tmpl_context.form_errors.items():
            msgs.append('{} for {}'.format(
                errmsg, VARIABLE_NAMES.get(val, val)))
        flash(' '.join(msgs), 'error')


class BaseGridController(BaseController):
    """ BaseController with griddata methods """

    def griddata(self, filler_class, filler_validators, **kw):
        """ Generic json function for grid data
        Based upon tgext.crud.controller.get_all
        """
        form_errors = {}
        key_validators = GRID_VALIDATORS.copy()
        key_validators.update(filler_validators)
        for key, validator in key_validators.items():
            try:
                form_value = kw.pop(key)
            except KeyError:
                continue
            try:
                form_value = validator.to_python(form_value)
            except Invalid as validator_msg:
                form_errors[key] = str(validator_msg)
            kw[key] = form_value
        if form_errors != {}:
            return dict(errors=form_errors)
        table_filler = filler_class(DBSession)
        return dict(value_list=table_filler.get_value(**kw))
