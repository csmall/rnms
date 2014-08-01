# -*- coding: utf-8 -*-


from nose.tools import ok_

from rnms.tests import TestController


class TestAnonymous(TestController):
    """
    Test to ensure that all exposed methods for the controllers
    are not visible to an anonymous (not logged in) user
    """
    application_under_test = 'main'

    def check_url(self, url):
        """ Internal method to check url redirects """
        resp = self.app.get(url, status=302)
        ok_(resp.location.startswith('http://localhost/login'))

    def test_attribute_noauth(self):
        """ Anonymous users to Attribute contorller are forced to login"""
        methods = ('', '1', '99', 'map', 'minigriddata', 'griddata',
                   'statuspie', 'att_summary', 'option')
        for m in methods:
            self.check_url('/attributes/'+m)
