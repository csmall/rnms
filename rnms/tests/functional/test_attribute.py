"""
Functional test suite for the Attribute controller.
"""
from rnms.tests import TestController, jqgrid_data_url


class TestAttributeController(TestController):

    def test_index(self):
        """ The Attribute index page is working """
        self.check_response('/attributes',
                            ('"url": "/attributes/griddata"',
                             ))

    def test_index_hostid_ok(self):
        """ Attribute index with good Host ID """
        self.check_response('/attributes?h=1',
                            ('"url": "/attributes/griddata"',
                             '"postData": {"h": 1}'))

    def test_index_hostid_neg(self):
        """ Attribute index with negative Host ID """
        self.check_response('/attributes?h=-1',
            ( 'Please enter a number that is 1 or greater for Host ID'))

    def test_index_hostid_notnum(self):
        """ Attribute index with non-numeric Host ID """
        self.check_response('/attributes?h=xyz',
            ( 'Please enter an integer value for Host ID'))

    def test_details_id_ok(self):
        """ Attribute detail page with valid ID """
        self.check_response('/attributes/1',
                            ('Attribute ID#1 not found',))

    def test_details_id_neg(self):
        """ Attribute Details with negative ID """
        self.check_response('/attributes/-1',
            ( 'Please enter a number that is 1 or greater for Attribute ID',))

    def test_details_nonnum_id(self):
        """ Attribute Details with non-numeric ID """
        self.check_response('/attributes/xyz',
            ( 'Please enter an integer value for Attribute ID',))

    def test_map_hostid_none(self):
        """ Attribute Map with no Host ID """
        self.check_response('/attributes/map',
            ('Attribute Map',))

    def test_map_hostid__ok(self):
        """ Attribute Map with ok Host ID """
        self.check_response('/attributes/map?h=1',
            ('Attribute Map',))

    def test_map_hostid_neg(self):
        """ Attribute Map with negative Host ID """
        self.check_response('/attributes/map?h=-1',
            ( 'Please enter a number that is 1 or greater for Host ID',))

    def test_map_hostid_notnum(self):
        """ Attribute Map with not-numeric Host ID """
        self.check_response('/attributes/map?h=abc',
            ( 'Please enter an integer value for Host ID',))

    def test_griddata_none(self):
        """ Attribute griddata with no ID """
        self.check_response(
            jqgrid_data_url('/attributes/griddata'),
            (r'{"total": 1, "page": 1, "entries": []}',))
