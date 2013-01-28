
"""
Testing of the SLAanalyzer object
"""
import mock
from nose.tools import eq_

from rnms import model
from rnms.lib.sla_analyzer import SLAanalyzer

class TestSlaAnalyzer(object):

    def setUp(self):
        self.sla_analyzer = SLAanalyzer()
        self.test_attribute, self.test_sla = self.make_att_sla(42)


    def make_att_sla(self,att_id):
        test_sla = mock.MagicMock(spec_set=model.Sla)
        test_sla.analyze = mock.Mock()

        test_attribute = mock.MagicMock(spec_sec=model.Attribute)
        test_attribute.sla = test_sla
        test_attribute.id = att_id
        test_attribute.display_name = 'Test Att #{}'.format(att_id)
        return (test_attribute, test_sla)

    def run_analyzer(self, attributes):
        model.Attribute.have_sla = mock.Mock(return_value=attributes)
        self.sla_analyzer.analyze()

    def test_no_attributes(self):
        self.run_analyzer([])
        eq_(self.test_sla.analyze.called, False)

    def test_one_att(self):
        """ Single Attribute is analyzed """
        self.test_attribute.is_down = mock.Mock(return_value=False)
        self.run_analyzer([self.test_attribute,])
        self.test_sla.analyze.assert_called_once_with(self.test_attribute)

    def test_called_two(self):
        """ Analyzer is called for both attributes """
        self.test_attribute.is_down = mock.Mock(return_value=False)
        second_att,second_sla = self.make_att_sla(43)
        second_att.is_down = mock.Mock(return_value=False)
        self.run_analyzer([self.test_attribute, second_att])
        self.test_sla.analyze.assert_called_once_with(self.test_attribute)
        second_sla.analyze.assert_called_once_with(second_att)

    def test_skip_down(self):
        """ Analyzer not run over a down attribute """
        self.test_attribute.is_down = mock.Mock(return_value=True)
        self.run_analyzer([self.test_attribute])
        eq_(self.test_sla.analyze.called, False)



