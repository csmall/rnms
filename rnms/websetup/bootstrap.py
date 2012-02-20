# -*- coding: utf-8 -*-

"""Setup the Rosenberg-NMS application"""

import logging
import re
from tg import config
from rnms import model
from rnms.websetup import database_data
import transaction

def bootstrap(command, conf, vars):
    """Place any commands to setup rnms here"""

    # <websetup.bootstrap.before.auth
    from sqlalchemy.exc import IntegrityError
    try:
        u = model.User()
        u.user_name = u'manager'
        u.display_name = u'Example manager'
        u.email_address = u'manager@somedomain.com'
        u.password = u'managepass'
    
        model.DBSession.add(u)
    
        g = model.Group()
        g.group_name = u'managers'
        g.display_name = u'Managers Group'
    
        g.users.append(u)
    
        model.DBSession.add(g)
    
        p = model.Permission()
        p.permission_name = u'manage'
        p.description = u'This permission give an administrative right to the bearer'
        p.groups.append(g)
    
        model.DBSession.add(p)
    
        u1 = model.User()
        u1.user_name = u'editor'
        u1.display_name = u'Example editor'
        u1.email_address = u'editor@somedomain.com'
        u1.password = u'editpass'
    
        model.DBSession.add(u1)
        model.DBSession.flush()
        transaction.commit()
    except IntegrityError:
        print 'Warning, there was a problem adding your auth data, it may have already been added:'
        import traceback
        print traceback.format_exc()
        transaction.abort()
        print 'Continuing with bootstrapping...'

    try:
        for row in database_data.alarm_states:
            a = model.AlarmState()
            (a.display_name, a.alarm_level, a.sound_in, a.sound_out, a.internal_state) = row
            model.DBSession.add(a)

        for row in database_data.attribute_types:
            at = model.AttributeType()
            (at.display_name, at.ad_validate, at.ad_enabled, at.ad_function,
                    at.ad_parameters, at.default_poller_id, 
                    at.rra_cf, at.rra_rows, ignore_step, at.default_graph_id,
                    at.break_by_card, ignore_handler, at.permit_manual_add,
                    at.default_sla_id, ignore_tools, at.required_sysobjid, fields, rrds
                    ) = row
            for field in fields:
                f = model.AttributeTypeField()
                (f.display_name, f.tag, f.position, f.description,f.showable_edit, f.showable_discovery, f.overwritable, f.tracked, f.default, f.parameters, f.backend) = field
                at.fields.append(f)
            # FIXME needs to process fields and rrds
            model.DBSession.add(at)


        for row in database_data.config_transfers:
            ct = model.ConfigTransfer(row[0], row[1])
            model.DBSession.add(ct)

        for row in database_data.autodiscovery_policies:
            p = model.AutodiscoveryPolicy()
            (p.display_name,p.default_poller,p.permit_add,p.permit_delete,
                    p.alert_delete,p.permit_modify,p.permit_disable,
                    p.skip_loopback,p.check_state,p.check_address)=row
            model.DBSession.add(p)

        for severity in database_data.event_severities:
            sv = model.EventSeverity(severity[0],severity[1],severity[2],severity[3])
            model.DBSession.add(sv)

        for row in database_data.event_types:
            et = model.EventType()
            (et.display_name, severity, et.text, et.showable, et.generate_id, et.up_event_id, et.alarm_duration, et.show_host) = row
            et.severity = model.EventSeverity.by_name(severity)
            #print("eseverity %s is %s" % (severity, et.severity))
            model.DBSession.add(et)

        # Logmatches
        logmatch_set = model.LogmatchSet(display_name=u'Default')
        model.DBSession.add(logmatch_set)

        for row in database_data.logfiles:
            lf = model.Logfile(row[0],row[1])
            lf.logmatchset = logmatch_set
            model.DBSession.add(lf)

        for row in database_data.logmatch_default_rows:
            try:
                lmr = model.LogmatchRow()
                (lmr.match_text, lmr.match_start, lmr.host_match, 
                    lmr.attribute_match, lmr.state_match, lmr.event_type_id,
                    fields) = row
                try:
                  lmr.match_sre = re.compile(row[0])
                except re.error as errmsg:
                    print "Cannot compile message \"%s\": %s" % (row[0],errmsg)
                    exit()
                lmr.logmatch_set = logmatch_set
                for field in fields:
                    lmf = model.LogmatchField()
                    (lmf.event_field_tag, lmf.field_match)=field
                    lmr.fields.append(lmf)
                model.DBSession.add(lmr)
            except Exception as errmsg:
                print "Cannot add row \"%s\": %s.\n" % (row[0], errmsg)
                exit()

        for row in database_data.slas:
            s = model.Sla()
            (s.display_name, s.alarm_state_id, s.event_text, s.event_id, s.threshold, s.attribute_type_id) = row
            model.DBSession.add(s)

        ps = model.PollerSet(u'No Polling')
        model.DBSession.add(ps)

        # Default Single Setup
        zone = model.Zone(u'Default Zone',u'default')
        model.DBSession.add(zone)
        host = model.Host('0.0.0.0','No Host')
        host.zone = zone
        model.DBSession.add(host)



        model.DBSession.flush()
        transaction.commit()
    except IntegrityError:
        print 'Warning, there was a problem adding your base data'
        import traceback
        print traceback.format_exc()
        transaction.abort()


    # <websetup.bootstrap.after.auth>
