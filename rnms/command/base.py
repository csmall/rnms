
class BaseCommand(object):
    """ Base Object for Rnms specific functions """

    def get_rnms_arguments(self, parser):
        """ Adds the standard arguments for all RNMS commands """
        parser.add_argument(
            '-c', '--config',
            action='store',
            dest='config',
            help='Specify the config file to use',
            default='production.ini',
            )

