# -*- coding: utf-8 -*-
"""Main Controller"""
from sqlalchemy import func

from tg import expose, flash, require, lurl, request, redirect, \
        tmpl_context, config, predicates
from tg.i18n import ugettext as _, lazy_ugettext as l_
from rnms import model
from rnms.controllers.secure import SecureController
#from tgext.admin.tgadminconfig import TGAdminConfig
from tgext.admin.controller import AdminController
from tw2.jqplugins.ui import set_ui_theme_name

from rnms.controllers.admin import MyAdminConfig#, AdminController2
from rnms.widgets.attribute import AttributeStatusPie, AttributeStatusBar
from rnms.widgets import MainMenu
from rnms.widgets.base import InfoBox
from rnms.model import DBSession, Attribute

from rnms.lib import states
from rnms.lib.base import BaseController
from rnms.lib.statistics import get_overall_statistics
from rnms.controllers.error import ErrorController
from rnms.controllers.events import EventsController
from rnms.controllers.graph import GraphController
from rnms.controllers.attributes import AttributesController
from rnms.controllers.hosts import HostsController
from rnms.controllers.zones import ZonesController

set_ui_theme_name(config['ui_theme'])
__all__ = ['RootController']

def get_attribute_pie():

    state_data = {}

    down_attributes = DBSession.query(Attribute).filter(Attribute.admin_state == states.STATE_DOWN)
    state_data[states.STATE_ADMIN_DOWN] = down_attributes.count()

    attributes = DBSession.query(func.count(Attribute.admin_state), Attribute.admin_state).group_by(Attribute.admin_state)
    for attribute in attributes:
        state_data[attribute[1]] = attribute[0]
    piebox = InfoBox()
    piebox.title = 'Attribute Status'
    piebox.child_widget = AttributeStatusPie()
    piebox.child_widget.state_data = state_data
    return piebox

class RootController(BaseController):
    """
    The root controller for the Rosenberg-NMS application.

    All the other controllers and WSGI applications should be mounted on this
    controller. For example::

        panel = ControlPanelController()
        another_app = AnotherWSGIApplication()

    Keep in mind that WSGI applications shouldn't be mounted directly: They
    must be wrapped around with :class:`tg.controllers.WSGIAppController`.

    """
    secc = SecureController()
    admin = AdminController(model, DBSession, config_type=MyAdminConfig)
    admin.allow_only = predicates.has_permission('manage')

    error = ErrorController()

    """ Rosenberg NMS Specific controllers below """
    attributes = AttributesController()
    events = EventsController()
    graphs = GraphController()
    hosts = HostsController()
    zones = ZonesController()


    def _before(self, *args, **kw):
        tmpl_context.project_name = "rnms"
        set_ui_theme_name(config['ui_theme'])

    @expose('rnms.templates.test')
    def test1(self):
        from tw2.jquery import jquery_js
        from rnms.widgets import MainMenu

        #mm = MainMenu(page='host')
        return {'text': 'texttext', 'jjs': jquery_js, 'mm': MainMenu,
                'page':'hosts'}
            
    @expose('rnms.templates.index')
    def index(self):
        """Handle the front-page."""
        statrows = get_overall_statistics()
        piebox = get_attribute_pie()
        statsbox = InfoBox()
        statsbox.title = 'Statistics'
        status_bar = AttributeStatusBar()
        return dict(page='index', main_menu=MainMenu,
                    piebox=piebox, statsbox=statsbox,
                    statrows=statrows, status_bar=status_bar)

    @expose('rnms.templates.about')
    def about(self):
        """Handle the 'about' page."""
        return dict(page='about', main_menu=MainMenu)

    @expose('rnms.templates.environ')
    def environ(self):
        """This method showcases TG's access to the wsgi environment."""
        return dict(page='environ', environment=request.environ)

    @expose('json')
    #@expose('rnms.templates.data')
    def data(self, **kw):
        """This method showcases how you can use the same controller for a data page and a display page"""
        return dict(page='data', params=kw)

    @expose('rnms.templates.index')
    #@require(predicates.has_permission('manage', msg=l_('Only for managers')))
    def manage_permission_only(self, **kw):
        """Illustrate how a page for managers only works."""
        return dict(page='managers stuff')

    @expose('rnms.templates.index')
    @require(predicates.is_user('editor', msg=l_('Only for the editor')))
    def editor_user_only(self, **kw):
        """Illustrate how a page exclusive for the editor works."""
        return dict(page='editor stuff')

    @expose('rnms.templates.login')
    def login(self, came_from=lurl('/')):
        """Start the user login."""
        login_counter = request.environ.get('repoze.who.logins', 0)
        if login_counter > 0:
            flash(_('Wrong credentials'), 'warning')
        return dict(page='login', login_counter=str(login_counter),
                    came_from=came_from)

    @expose()
    def post_login(self, came_from=lurl('/')):
        """
        Redirect the user to the initially requested page on successful
        authentication or redirect her back to the login page if login failed.

        """
        if not request.identity:
            login_counter = request.environ.get('repoze.who.logins', 0) + 1
            redirect('/login',
                params=dict(came_from=came_from, __logins=login_counter))
        userid = request.identity['repoze.who.userid']
        flash(_('Welcome back, %s!') % userid)
        redirect(came_from)

    @expose()
    def post_logout(self, came_from=lurl('/')):
        """
        Redirect the user to the initially requested page on logout and say
        goodbye as well.

        """
        flash(_('We hope to see you soon!'))
        redirect(came_from)
