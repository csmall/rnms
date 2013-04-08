
"""
Testing of the SLAanalyzer object
"""
import mock
from nose.tools import eq_

from rnms import model
from rnms.lib.sla_analyzer import SLAanalyzer

class TestSlaAnalyzer(object):

    def setUp(self):
        self.obj = SLAanalyzer()
        self.obj.logger = mock.Mock()
        self.test_attribute, self.test_sla = self.make_att_sla(42)
        self.test_analyze_attribute = mock.Mock()


    def make_att_sla(self,att_id):
        test_sla = mock.MagicMock(spec_set=model.Sla)

        test_attribute = mock.MagicMock(spec_sec=model.Attribute)
        test_attribute.sla = test_sla
        test_attribute.id = att_id
        test_attribute.display_name = 'Test Att #{}'.format(att_id)
        return (test_attribute, test_sla)

    def run_mock_analyzer(self, attributes):
        self.obj.analyze_attribute = self.test_analyze_attribute
        model.Attribute.have_sla = mock.Mock(return_value=attributes)
        self.obj.analyze()#self.test_sla, attributes)

    def assert_mock_analyzer(self, attributes):
        self.obj.analyze_attribute.assert_called_once_with(attributes)


    def test_no_attributes(self):
        """ Analyzer works with no attributes """
        self.run_mock_analyzer([])
        eq_(self.obj.analyze_attribute.called, False)

    def test_one_att(self):
        """ Single Attribute is analyzed """
        self.test_attribute.is_down = mock.Mock(return_value=False)
        self.run_mock_analyzer([self.test_attribute,])
        self.assert_mock_analyzer(self.test_attribute)

    def test_called_two(self):
        """ Analyzer is called for both attributes """
        self.test_attribute.is_down = mock.Mock(return_value=False)
        second_att,second_sla = self.make_att_sla(43)
        second_att.is_down = mock.Mock(return_value=False)
        self.run_mock_analyzer((self.test_attribute, second_att))
        eq_(self.obj.analyze_attribute.call_args_list[0][0], (self.test_attribute,))
        eq_(self.obj.analyze_attribute.call_args_list[1][0], (second_att,))

    def test_skip_down(self):
        """ Analyzer not run over a down attribute """
        self.test_attribute.is_down = mock.Mock(return_value=True)
        self.run_mock_analyzer([self.test_attribute])
        eq_(self.obj.analyze_attribute.called, False)



