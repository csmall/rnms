
logfiles = (
    (u'Database', u''),
    (u'Messages', u'/var/log/messages'),
    )

logmatch_default_rows = (
    #match_text,
    #  start,host, attr, state, event_id,i (f1name,f1match,...)
    (u'%BGP-5-ADJCHANGE: neighbour (\S+) (\S+)$',
        False, None, 1, 2, 'bgp_status', None),
    (u'%BGP-3-NOTIFICATION: (\S+ \S+) neighbor (\S+) \S+ \(([^)]+)\)',
        False, None, 2, None, 'bgp_notify', (('info', 3), ('direction', 1))),
    (u'%CDP-4-DUPLEX_MISMATCH: duplex mismatch discovered on (\S+) \(([^)]+)\)'
        ' with (\S+ \S+) \(([^)]+)\)',
        False, None, 1, None, 'duplex_mismatch',
        (('our_dup', 2), ('their_int', 3), ('their_dup', 4), )),
    (u'%CLEAR-5-COUNTERS: Clear counter on \S+ (\S+) by (\S+)',
        False, None, 1, None, 'clear_counters', (('user', 2, ), )),
    (u'%CONTROLLER-5-UPDOWN: '
     'Controller \S+ (\S+), changed state to (\S+) \([^)]+\)$',
        False, None, 1, 2, 'controller_status', (('info', 3), )),
    (u'%LINK-3-UPDOWN: Interface (\S+), changed state to (\S+)',
        False, None, 1, 2, 'interface_link', None),
    (u'%LINK-5-CHANGED: Interface (\S+), changed state to (\S+)',
        False, None, 1, 2, 'interface_shutdown', None),
    (u'%LINEPROTO-5-UPDOWN: Line protocol on Interface (\S+), changed state to (\S+)',
        False, None, 1, 2, 'interface_protocol', None),
    (u'%SYS-5-CONFIG_I: Configured from \S+ by (\S+) on \S+ \((\S+)\)',
        False, None, None, None, 'configuration',
        (('user', 1), ('source', 2))),
    (u'%SYS-5-(?:RESTART|RELOAD): (.+)$',
        False, None, None, None, 'environment', (('info', 1), )),
    (u'%SEC-6-IPACCESSLOG(?:DP|P|NP|S): list (.+)$',
        False, None, None, None, 'acl', (('info', 1), )),
    (u'EXCESSCOLL: (\S+)',
        False, None, 1, None, 'collision', None),
    )
