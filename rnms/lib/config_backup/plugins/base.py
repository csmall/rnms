
class ConfigBackupPlugin(object):
    """ Base Class for all Configuration Backup plugins """

    def start(self, parent, host):
        """ Start the transfer """
        raise NotImplemented()

    def wait_transfer(self, host, **kw):
        """ Wait for the transfer, this will return
        True if it went ok, False for error
        Some other method will call parent.transfer_callback
        once the transfer is finished or failed
        """
        raise NotImplemented()
