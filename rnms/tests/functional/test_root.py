# -*- coding: utf-8 -*-
"""
Functional test suite for the root controller.

This is an example of how functional tests can be written for controllers.

As opposed to a unit-test, which test a small unit of functionality,
functional tests exercise the whole application and its WSGI stack.

Please read http://pythonpaste.org/webtest/ for more information.

"""

from nose.tools import ok_

from rnms.tests import TestController


class TestRootController(TestController):
    """Tests for the method in the root controller."""

    def notest_index(self):
        """The front page is working properly"""
        self.check_response('/',
                            ('NMS Status', 'Attribute Status'))

    def test_about(self):
        """ About information page is working correctly """
        self.check_response('/about',
                            ('About RoseNMS',))

    def test_environ(self):
        """Displaying the wsgi environ works"""
        response = self.app.get('/environ.html')
        ok_('The keys in the environment are: ' in response)
