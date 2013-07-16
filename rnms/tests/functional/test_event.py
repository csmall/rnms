"""
Functional test suite for the event controller.
"""
from rnms.tests import TestController

class TestEventController(TestController):

    def test_index(self):
        """ The event index page is working """
        self.check_response_as_admin('/events',
                            ('"url": "/events/griddata"',
                             'Rosenberg NMS: Event List'))
    def test_index_attid_ok(self):
        """ The event index page is working with good attribute """
        self.check_response_as_admin('/events?a=1',
                            ('"url": "/events/griddata?a=1"',
                             'Rosenberg NMS: Event List'))
    
    def test_index_attid_neg(self):
        """ The event index page with negative number """
        self.check_response_as_admin('/events?a=-1',
            ( 'Please enter a number that is 1 or greater for Attribute ID'))

    def test_index_attid_notnum(self):
        """ The event index page with negative number """
        self.check_response_as_admin('/events?a=xyz',
            ( 'Please enter an integer value for Attribute ID'))

    def test_index_hostid_ok(self):
        """ The event index page is working with good host ID """
        self.check_response_as_admin('/events?h=1',
                            ('"url": "/events/griddata?h=1"',
                             'Rosenberg NMS: Event List'))
    
    def test_index_hostid_neg(self):
        """ The event index page with negative host id """
        self.check_response_as_admin('/events?h=-1',
            ( 'Please enter a number that is 1 or greater for Host ID'))

    def test_index_hostid_notnum(self):
        """ The event index page with non-numeric Host ID"""
        self.check_response_as_admin('/events?h=xyz',
            ( 'Please enter an integer value for Host ID'))

