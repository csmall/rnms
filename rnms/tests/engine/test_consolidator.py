
import mock
#from nose.tools import eq_

#from rnms import model
from rnms.tests import setup_db, teardown_db
from rnms.lib import consolidate
#from rnms.lib.consolidate.logfiles import consolidate_logfiles
#from rnms.lib.consolidate.alarms import check_alarm_stop_time, check_alarm_triggers

def setup():
    setup_db()


def teardown():
    teardown_db()

class TestConsolidator(object):

    def setUp(self):
        self.obj = consolidate.Consolidator()
        self.obj.logger = mock.Mock()

    def NOTtest_main_loop(self):
        self.obj.consolidate()
