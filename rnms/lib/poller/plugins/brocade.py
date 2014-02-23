
BROCADE_FCSTATES = {
    1: ('down', 'No card present'),
    2: ('down', 'No GBIC module'),
    3: ('down', 'Laser Fault'),
    4: ('down', 'No light received'),
    5: ('down', 'Not in sync'),
    6: ('up', 'In sync'),
    7: ('down', 'Port marked faulty'),
    8: ('down', 'Port locked to reference signal')
    }


def poll_brocade_fcport_phystate(poller_buffer, parsed_params, **kw):
    """
    Determine the Physical state of a Fiber Channel port on a Brocade
    switch
    """
    oid = (1, 3, 6, 1, 4, 1, 1588, 2, 1, 1, 1, 6, 2, 1, 3)
    if kw['attribute'].index == '':
        return False
    inst_oid = oid + (int(kw['attribute'].index),)
    return kw['pobj'].snmp_engine.get_int(
        kw['attribute'].host, inst_oid, cb_brocade_fcport_phystate, **kw)


def cb_brocade_fcport_phystate(value, error, pobj, attribute, **kw):
    if value is None:
        pobj.poller_callback(attribute.id, None)
        return
    pobj.poller_callback(
        attribute.id,
        BROCADE_FCSTATES.get(value, "Unknown status {}".format(value)))
