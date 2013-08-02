# -*- coding: utf-8 -*-
"""Unit and functional test suite for rnms."""

from os import getcwd

from paste.deploy import loadapp
from webtest import TestApp
from nose.tools import assert_true, eq_
import json

from gearbox.commands.setup_app import SetupAppCommand
from tg import config
from tg.util import Bunch

from rnms import model

__all__ = ['setup_app', 'setup_db', 'teardown_db', 'TestController']

application_name = 'main_without_authn'


def load_app(name=application_name):
    """Load the test application."""
    return TestApp(loadapp('config:test.ini#%s' % name, relative_to=getcwd()))


def setup_app():
    """Setup the application."""
    cmd = SetupAppCommand(Bunch(options=Bunch(verbose_level=1)), Bunch())
    cmd.run(Bunch(config_file='config:test.ini', section_name=None))

def setup_db():
    """Create the database schema (not needed when you run setup_app)."""
    engine = config['tg.app_globals'].sa_engine
    model.init_model(engine)
    model.metadata.create_all(engine)


def teardown_db():
    """Destroy the database schema."""
    engine = config['tg.app_globals'].sa_engine
    model.metadata.drop_all(engine)


class TestController(object):
    """Base functional test case for the controllers.

    The rnms application instance (``self.app``) set up in this test
    case (and descendants) has authentication disabled, so that developers can
    test the protected areas independently of the :mod:`repoze.who` plugins
    used initially. This way, authentication can be tested once and separately.

    Check rnms.tests.functional.test_authentication for the repoze.who
    integration tests.

    This is the officially supported way to test protected areas with
    repoze.who-testutil (http://code.gustavonarea.net/repoze.who-testutil/).

    """

    application_under_test = application_name

    def setUp(self):
        """Setup test fixture for each functional test method."""
        self.app = load_app(self.application_under_test)
        setup_app()

    def tearDown(self):
        """Tear down test fixture for each functional test method."""
        model.DBSession.remove()
        teardown_db()

    def check_json_response(self, url, expected_data):
        """ Get the given url and check the JSON response """
        environ = {'REMOTE_USER': 'manager'}
        response = self.app.get(url, extra_environ=environ, status=200)
        json_data = json.loads(response)
        for k,v in expected_data:
            try:
                assert_true(k in json_data)
            except AssertionError:
                raise AssertionError('Key not found in data:'+k)
            eq_(json_data[k] == v)

    def check_response(self, url, msgs):
        """ Get the given url and check that the msgs appear in reponse """
        environ = {'REMOTE_USER': 'manager'}
        response = self.app.get(url, extra_environ=environ, status=200)
        for msg in  msgs:
            try:
                assert_true(msg in response)
            except AssertionError:
                print response
                raise AssertionError('Not found:'+msg)


JQGRID_STD_ATTRIBS={
    '_search': False,
    'nd': 1234567890,
    'rows': 15,
    'page': 1,
    'sidx': '',
    'sord': 'asc',}

def jqgrid_data_url(base_url, attribs={}):
    """ Return a url with the standard jqgrid attributes """
    my_attribs = JQGRID_STD_ATTRIBS.copy()
    my_attribs.update(attribs)
    return '{}?{}'.format(
        base_url,
        '&'.join('{}={}'.format(k,v) for k,v in my_attribs.items())
    )

