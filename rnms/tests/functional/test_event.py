"""
Functional test suite for the event controller.
"""
from rnms.tests import TestController


class TestEventController(TestController):

    def test_index(self):
        """ The event index page is working """
        self.check_response('/events',
                            ('data-url="/events/tabledata.json"',
                             'Event List'))

    def test_index_attid_ok(self):
        """ The event index page is working with good attribute """
        self.check_response('/events?a=1',
                            ('data-url="/events/tabledata.json"',
                             'params[\'a\'] = \'1\';',
                             'Event List'))

    def test_index_attid_neg(self):
        """ The event index page with negative number """
        self.check_response(
            '/events?a=-1',
            ('Please enter a number that is 1 or greater for Attribute ID'))

    def test_index_attid_notnum(self):
        """ The event index page with negative number """
        self.check_response(
            '/events?a=xyz',
            ('Please enter an integer value for Attribute ID'))

    def test_index_hostid_ok(self):
        """ The event index page is working with good host ID """
        self.check_response('/events?h=1',
                            ('data-url="/events/tabledata.json"',
                             'params[\'h\'] = \'1\';',
                             'Event List'))

    def test_index_hostid_neg(self):
        """ The event index page with negative host id """
        self.check_response(
            '/events?h=-1',
            ('Please enter a number that is 1 or greater for Host ID'))

    def test_index_hostid_notnum(self):
        """ The event index page with non-numeric Host ID"""
        self.check_response(
            '/events?h=xyz',
            ('Please enter an integer value for Host ID'))
