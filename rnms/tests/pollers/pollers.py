
import mock

from nose.tools import eq_
from rnms.lib import pollers
from rnms.tests.models import ModelTest

class TestPollers(ModelTest):

    def setUp(self):
        super(TestPollers, self).setUp()
        self.attribute = mock.Mock()
        self.attribute.host = mock.Mock()
        self.poller = mock.Mock()
        self.poller.ntp_client = mock.Mock()
        self.poller.ntp_client.get_peers = mock.Mock(return_value=True)
        self.poller_buffer = {}

    def test_ntp_client_poll(self):
        pollers.poll_ntp_client(poller_buffer, pobj=self.poller, attribute=self.attribute)
        self.ntp_client.get_peers.assert_called_once()
        

