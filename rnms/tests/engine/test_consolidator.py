
import mock
from nose.tools import eq_

from rnms import model
from rnms.tests import setup_db, teardown_db
from rnms.lib import consolidate
from rnms.lib.consolidate.logfiles import consolidate_logfiles
from rnms.lib.consolidate.alarms import check_alarm_stop_time, check_alarm_triggers

def setup():
    setup_db()


def teardown():
    teardown_db()

class TestAlarmConsolidator(object):

    def setUp(self):
        self.logger = mock.Mock()
        self.test_attribute = model.Attribute(display_name='Test Attribute')
        self.test_alarm_state = model.AlarmState()
        self.test_alarm_state.display_name = u'Test Alarm State'
        self.test_alarm_state.internal_state = 0
        self.test_alarm = model.Alarm()
        self.test_alarm.attribute = self.test_attribute
        self.test_alarm.alarm_state = self.test_alarm_state
        model.DBSession.add(self.test_alarm)
        model.DBSession.flush()

    def NOtest_foo(self):
        consolidate_alarms(self.logger)

class TestConsolidator(object):

    def setUp(self):
        self.obj = consolidate.Consolidator()
        self.obj.logger = mock.Mock()

    def NOTtest_main_loop(self):
        self.obj.consolidate()
