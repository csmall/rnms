# -*- coding: utf-8 -*-
"""Unit and functional test suite for Rosenberg-NMS."""

from os import path

from tg import config
import json
from paste.deploy import loadapp
from paste.script.appinstall import SetupCommand
from routes import url_for
from webtest import TestApp
from nose.tools import assert_true, eq_


from rnms import model
import warnings

__all__ = ['setup_db', 'teardown_db', 'TestController', 'url_for']
def setup_db():
    """Method used to build a database"""
    engine = config['pylons.app_globals'].sa_engine
    model.init_model(engine)
    model.metadata.create_all(engine)

def teardown_db():
    """Method used to destroy a database"""
    engine = config['pylons.app_globals'].sa_engine
    model.metadata.drop_all(engine)

class TestController(object):
    """
    Base functional test case for the controllers.
    
    The Rosenberg-NMS application instance (``self.app``) set up in this test 
    case (and descendants) has authentication disabled, so that developers can
    test the protected areas independently of the :mod:`repoze.who` plugins
    used initially. This way, authentication can be tested once and separately.
    
    Check rnms.tests.functional.test_authentication for the repoze.who
    integration tests.
    
    This is the officially supported way to test protected areas with
    repoze.who-testutil (http://code.gustavonarea.net/repoze.who-testutil/).
    
    """
    
    application_under_test = 'main_without_authn'
    
    def setUp(self):
        """Method called by nose before running each test"""
        # Loading the application:
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        conf_dir = config.here
        wsgiapp = loadapp('config:test.ini#%s' % self.application_under_test,
                          relative_to=conf_dir)
        self.app = TestApp(wsgiapp)
        # Setting it up:
        test_file = path.join(conf_dir, 'test.ini')
        cmd = SetupCommand('setup-app')
        cmd.run([test_file])

    def tearDown(self):
        """Method called by nose after running each test"""
        # Cleaning up the database:
        model.DBSession.remove()
        teardown_db()

    def check_json_response_as_admin(self, url, expected_data):
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

    def check_response_as_admin(self, url, msgs):
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

