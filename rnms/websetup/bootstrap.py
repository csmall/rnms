# -*- coding: utf-8 -*-

"""Setup the Rosenberg-NMS application"""

import logging
import re
from tg import config
from rnms import model
from rnms.websetup import database_data
import transaction
from sqlalchemy.sql import not_

def bootstrap(command, conf, vars):
    """Place any commands to setup rnms here"""
    used_event_types = []

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
        u1.user_name = u'customer'
        u1.display_name = u'Default Customer'
        u1.email_address = u'customer@somedomain.com'
        u1.password = u'customer'
    
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

        atype_psets = []
        for row in database_data.attribute_types:
            at = model.AttributeType()
            #FIXME - The poller set must be a name not number at this point
            (at.display_name, at.ad_validate, at.ad_enabled, at.ad_command,
                    at.ad_parameters, default_poller_set,
                    at.rra_cf, at.rra_rows, ignore_step, at.default_graph_id,
                    at.break_by_card, ignore_handler, at.permit_manual_add,
                    at.default_sla_id, ignore_tools, at.required_sysobjid, fields, rrds
                    ) = row
            atype_psets.append((at.display_name, default_poller_set))
            field_position = 0
            for field in fields:
                f = model.AttributeTypeField()
                (f.display_name, f.tag, f.description,f.showable_edit, f.showable_discovery, f.overwritable, f.tracked, f.default_value, f.parameters, f.backend) = field
                f.position = field_position
                field_position += 1
                at.fields.append(f)
            rrd_position = 0
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
            (p.display_name,p.set_poller,p.permit_add,p.permit_delete,
                    p.alert_delete,p.permit_modify,p.permit_disable,
                    p.skip_loopback,p.check_state,p.check_address)=row
            model.DBSession.add(p)

        for severity in database_data.event_severities:
            sv = model.EventSeverity(severity[0],severity[1],severity[2],severity[3])
            model.DBSession.add(sv)

        for row in database_data.event_types:
            et = model.EventType()
            try:
                (et.display_name, severity, et.tag, et.text, et.generate_alarm, et.up_event_id, et.alarm_duration, et.showable, et.show_host) = row
            except ValueError as errmsg:
                print("Bad event_type \"{0}\".\n{1}".format(row, errmsg))
                exit()
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
                    lmr.attribute_match, lmr.state_match, event_tag,
                    fields) = row
                lmr.event_type = model.EventType.by_tag(event_tag)
                if lmr.event_type is None:
                    print "Bad EventType tag \"{0}\" in LogMatchRow {1}".format(event_tag, lmr.match_text)
                    exit()
                used_event_types.append(lmr.event_type.id)
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

        # Graph Types
        for row in database_data.graph_types:
            gt = model.GraphType()
            (gt.display_name, atype_name, gt.title, gt.vertical_label, gt.extra_options, graph_defs, graph_vnames, graph_lines ) = row
            attribute_type = model.AttributeType.by_display_name(atype_name)
            if attribute_type is None:
                raise ValueError("Attribute Type {} not found in GraphType {}".format(atype_name, gt.display_name))
            gt.attribute_type = attribute_type
            for graph_def in graph_defs:
                at_rrd = model.AttributeTypeRRD.by_name(attribute_type, graph_def[1])
                if at_rrd is None:
                    raise ValueError("AttributeTypeRRD {} not found in GraphType {}".format(graph_def[1], gt.display_name))
                gt_def = model.GraphTypeDef(gt, graph_def[0], at_rrd)
                gt.defs.append(gt_def)

            position=0
            for vname in graph_vnames:
                vn = model.GraphTypeVname()
                (def_type, vn.name, vn.expression) = vname
                vn.set_def_type(def_type)
                vn.position = position
                gt.vnames.append(vn)

            position = 0
            for graph_line in graph_lines:
                gl = model.GraphTypeLine()
                gl.position = position

                if graph_line[0] == 'COMMENT':
                    gl.set_comment(*graph_line[1:])
                elif graph_line[0] == 'HRULE':
                    gl.set_hrule(*graph_line[1:])
                else:
                    vname = gt.vname_by_name(graph_line[1])
                    if vname is None:
                        raise ValueError('Vname {} not found in GraphType {}'.format(graph_line[1], gt.display_name))
                    if graph_line[0] == 'PRINT':
                        gl.set_print(vname, graph_line[2])
                    elif graph_line[0] == 'GPRINT':
                        gl.set_gprint(vname, graph_line[2])
                    elif graph_line[0] == 'VRULE':
                        gl.set_vrule(vname, *graph_line[2:])
                    elif graph_line[0] == 'LINE':
                        gl.set_line(vname, *graph_line[2:])
                    elif graph_line[0] == 'AREA':
                        gl.set_area(vname, *graph_line[2:])
                    elif graph_line[0] == 'TICK':
                        gl.set_tick(vname, *graph_line[3:])
                    else:
                        raise ValueError('Bad GraphTypeLine type {} in GraphType {}'.format(graph_line[0], gt.display_name))
                position += 1
                gt.lines.append(gl)

            model.DBSession.add(gt)



        # Pollers
        for row in database_data.pollers:
            p = model.Poller()
            (p.field, dn, p.command, p.parameters) = row
            p.display_name = unicode(dn)
            model.DBSession.add(p)

        for row in database_data.backends:
            be = model.Backend()
            (be.display_name, be.command, be.parameters) = row
            if be.command == 'event':
                parms = be.parameters.split(',')
                event_type = model.EventType.by_tag(parms[0])
                if event_type is None:
                    raise ValueError("EventType {0} not found in backend {1}".format(parms[0], be.display_name))
                    exit()
                used_event_types.append(event_type.id)
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
        # Now that the PollerSets are in, we can backfill the default
        # PollerSet for an AttributeType
        for at_name,ps_name in atype_psets:
            ps = model.PollerSet.by_display_name(ps_name)
            if ps is None:
                raise ValueError("Bad default PollerSet name \"{}\" for AttributeType {}.".format(ps_name, at_name))
            model.DBSession.query(model.AttributeType).filter(model.AttributeType.display_name == at_name).update({'default_poller_set_id': ps.id})

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
    print "\n\n------------------------------------------------------------------------\n"
    print "Validation of data"
    print "Unused Event Types: {0}".format(', '.join([ et.display_name for et in model.DBSession.query(model.EventType).filter(not_(model.EventType.id.in_(used_event_types))).all()]))
