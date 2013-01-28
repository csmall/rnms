import mock
from nose.tools import eq_

from rnms import model
from rnms.lib.sla_analyzer import SLAanalyzer

""" Tests of Numeric string parser """
# (887891 * 100) / 0 - 80
# (0 + 0 + 0) * 100 / (0 + 0 + 0 + 0) - 80
# "0 * 100 / (0 + 0)
class TestSlaAnalyzer(object):
    pass #FIXME
