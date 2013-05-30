# Constants - used for oper and adminm statates
STATE_UP = 1
STATE_DOWN = 2
STATE_TESTING = 3
STATE_UNKNOWN = 4
STATE_ALERT = 5

# This is strictly not a state but often used
STATE_ADMIN_DOWN = 99

STATE_NAMES = {
        STATE_UP:       'up',
        STATE_DOWN:     'down',
        STATE_TESTING:  'testing',
        STATE_UNKNOWN:  'unknown',
        STATE_ALERT:    'alert',
        STATE_ADMIN_DOWN: 'admin down',
        }

def state_name(val):
    """ Return the state name for the given value, if known """
    try:
        return STATE_NAMES[int(val)]
    except (ValueError, KeyError):
        pass
    return 'Unknown state {}'.format(val)
