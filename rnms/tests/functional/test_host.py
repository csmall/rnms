"""
Functional test suite for the Host controller.
"""
from rnms.tests import TestController

class TestHostController(TestController):

    def test_index(self):
        """ The event index page is working """
        self.check_response('/hosts',
                            ('"url": "/hosts/griddata"',
                             ))

    def test_details_id_ok(self):
        """ Host detail page with valid ID """
        self.check_response('/hosts/1',
                            ('Host Details',
                             'Attribute Status'))

    def test_details_id_neg(self):
        """ Host Details with negative ID """
        self.check_response('/hosts/-1',
            ( 'Please enter a number that is 1 or greater for Host ID'))

    def test_details_nonnum_id(self):
        """ Host Details with non-numeric ID """
        self.check_response('/hosts/xyz',
            ( 'Please enter an integer value for Host ID'))


    def test_map_nozone(self):
        """ Host Map with no zone """
        self.check_response('/hosts/map',
            ('Host Map',))

    def test_map_zone_ok(self):
        """ Host Map with ok zone ID """
        self.check_response('/hosts/map?z=1',
            ('Host Map',))

    def test_map_zone_neg(self):
        """ Host Map with negative Zone ID """
        self.check_response('/hosts/map?z=-1',
            ( 'Please enter a number that is 1 or greater for Zone ID'))

    def test_map_nonnum_id(self):
        """ Host Details with non-numeric ID """
        self.check_response('/hosts/map?z=abc',
            ( 'Please enter an integer value for Zone ID'))


