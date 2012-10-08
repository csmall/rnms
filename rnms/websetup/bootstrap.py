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
            field_position = 1
            for field in fields:
                f = model.AttributeTypeField()
                (f.display_name, f.tag, f.description,f.showable_edit, f.showable_discovery, f.overwritable, f.tracked, f.default_value, f.parameters, f.backend) = field
                f.position = field_position
                field_position += 1
                at.fields.append(f)
            rrd_position = 1
            for rrd in rrds:
                r = model.AttributeTypeRRD()
                (r.display_name, r.name, r.data_source_type, r.range_min, r.range_max, r.range_max_field) = rrd
                r.position = rrd_position
                rrd_position += 1
                at.rrds.append(r)
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
            (et.display_name, severity, et.text, et.generate_alarm, et.up_event_id, et.alarm_duration, et.showable, et.show_host) = row
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

        for row in database_data.sla_conditions:
            sc = model.SlaCondition()
            (sc.display_name, sc.expression, sc.oper, sc.limit, sc.show_info, sc.show_expression, sc.show_unit) = row
            model.DBSession.add(sc)

        for row in database_data.slas:
            s = model.Sla()
            (s.display_name, s.alarm_state_id, s.event_text, event_id, s.threshold, s.attribute_type_id, sla_rows) = row
            s.event_type_id = 10 # SLA evne_type
            model.DBSession.add(s)
            position=1
            for sla_row in sla_rows:
                sr = model.SlaRow(s,show_result=sla_row[1], position=position)
                sr.sla_condition_id = sla_row[0]
                position += 1
                model.DBSession.add(sr)

        # Pollers
        for row in database_data.pollers:
            p = model.Poller()
            (p.field, dn, p.command, p.parameters) = row
            p.display_name = unicode(dn)
            model.DBSession.add(p)

        for row in database_data.backends:
            be = model.Backend()
            (be.display_name, be.command, be.parameters) = row
            model.DBSession.add(be)

        for row in database_data.poller_sets:
            (ps_name, at_name, poller_rows) = row
            atype = model.AttributeType.by_display_name(at_name)
            if atype is None:
                raise ValueError("Attribute type {0} not found.".format(at_name))
            ps = model.PollerSet(ps_name)
            ps.attribute_type = atype
            poller_row_pos = 0
            default_backend = model.Backend.default()
            for poller_row in poller_rows:
                pr_poller = model.Poller.by_display_name(poller_row[0])
                if pr_poller is None:
                    raise ValueError("Bad poller name \"{0}\".".format(poller_row[0]))
                if poller_row[1] == u'':
                    pr_backend = default_backend
                else:
                    pr_backend = model.Backend.by_display_name(poller_row[1])
                if pr_backend is None:
                    raise ValueError("Bad backend name \"{0}\".".format(poller_row[1]))
                pr = model.PollerRow()
                pr.poller = pr_poller
                pr.backend = pr_backend
                pr.position = poller_row_pos
                poller_row_pos += 1
                ps.poller_rows.append(pr)
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
