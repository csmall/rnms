# -*- coding: utf-8 -*-

"""Setup the Rosenberg-NMS application"""

import logging
import re
import transaction
from sqlalchemy.sql import not_
from sqlalchemy.exc import IntegrityError

from rnms import model
from rnms.websetup import database_data

logger  = logging.getLogger('rnms')

def bootstrap(command, conf, vars):
    """Place any commands to setup rnms here"""

    # <websetup.bootstrap.before.auth
    try:

        for perm in database_data.permissions:
            p = model.Permission()
            (p.permission_name, p.description) = perm
            model.DBSession.add(p)

        for grp in database_data.groups:
            g = model.Group()
            (g.group_name, g.display_name, perms) = grp
            for perm_name in perms:
                p = model.Permission.by_name(perm_name)
                if p is None:
                    raise ValueError(
                        'Perm name {} not known in group {}'.format(
                            perm_name, g.group_name))
                p.groups.append(g)
            model.DBSession.add(g)

    
        model.DBSession.add(g)

        u = model.User()
        u.user_name = u'manager'
        u.display_name = u'Example manager'
        u.email_address = u'manager@somedomain.com'
        u.password = u'managepass'

        g = model.Group.by_group_name('System Admin')
        g.users.append(u)
        model.DBSession.add(u)

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

    b = BootStrapper()
    b.create()
    #b.validate()
    try:

        # SNMP Enterprises
        for ent in database_data.snmp_enterprises:
            e = model.SNMPEnterprise(ent[0], ent[1], ent[2])
            for device in ent[3]:
                d = model.SNMPDevice(e,device[0],device[1])
                model.DBSession.add(d)
            model.DBSession.add(e)
        model.DBSession.flush()
        transaction.commit()
    except IntegrityError:
        print 'Warning, there was a problem adding your base data'
        import traceback
        print traceback.format_exc()
        transaction.abort()

    # <websetup.bootstrap.after.auth>
class BootStrapper(object):
    models = ('defaults', 'autodiscovery', 'severities', 'event_states', 'config_transfers',
            'event_types',
            'logmatches', 'snmp_communities',
            'attribute_types', 'graph_types', 'slas',
            'pollers', 'backends', 'poller_sets', 'triggers'

            )

    def __init__(self):
        self.atype_refs = {}
        self.used_event_types = []
        self.used_sla_conditions = []

    def _commit(self, msg):
        try:
            model.DBSession.flush()
            transaction.commit()
        except IntegrityError as errmsg:
            transaction.abort()
            logger.error('Problem creating %s: %s', msg, errmsg)
            #import traceback
            #print traceback.format_exc()
            exit()

    def create(self):
        for m in self.models:
            func = getattr(self, 'create_{}'.format(m))
            func()
            self._commit(m)

        # Some foreign key fixes
        self.fix_attribute_types()

    def validate(self):
        print "\n\n------------------------------------------------------------------------\n"
        print "Validation of data"
        print "Unused Event Types: {0}".format(', '.join([ et.display_name for et in model.DBSession.query(model.EventType).filter(not_(model.EventType.id.in_(self.used_event_types))).all()]))

    def create_defaults(self):
        """
        Any objects that require a specific ID, such as Default Hosts or Admin
        Event types need to be defined here
        """
        zone = model.Zone(u'Default Zone',u'default')
        model.DBSession.add(zone)

        host = model.Host('0.0.0.0','No Host')
        host.zone = zone
        model.DBSession.add(host)

        sla = model.Sla()
        sla.display_name = u'No SLA'
        model.DBSession.add(sla)

        gt = model.GraphType()
        gt.display_name = u'No Graph'
        model.DBSession.add(gt)

        ct = model.ConfigTransfer(display_name=u'No Transfer')
        model.DBSession.add(ct)

    def create_event_states(self):
        for row in database_data.event_states:
            a = model.EventState()
            (a.display_name, a.priority, a.sound_in, a.sound_out,
             a.internal_state, severity_name) = row
            a.severity = model.Severity.by_name(severity_name)
            if a.severity is None:
                raise ValueError('Bad Severity {} in EventState {}'.format(
                    severity_name, a.display_name))
            model.DBSession.add(a)

    def create_attribute_types(self):
        for row in database_data.attribute_types:
            at = model.AttributeType()
            try:
                (at.display_name, at.ad_command,
                    at.ad_parameters, at_ad_validate, at.ad_enabled, 
                    default_poller_set, default_sla, default_graph,
                    at.rra_cf, at.rra_rows,
                    at.break_by_card, at.permit_manual_add,
                    at.required_sysobjid, fields, rrds
                    ) = row
            except ValueError:
                print "problem with row", row
                raise
            self.atype_refs[at.display_name] = (
                    default_poller_set, default_sla, default_graph)
            model.DBSession.add(at)

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
    
    def fix_attribute_types(self):
        default_sla = model.Sla.by_display_name(u'No SLA')
        default_gt = model.GraphType.by_display_name(u'No Graph')
        for at_name,at_refs in self.atype_refs.items():
            ps = model.PollerSet.by_display_name(at_refs[0])
            if ps is None:
                raise ValueError("Bad default PollerSet name \"{}\" for AttributeType {}.".format(at_refs[0], at_name))
            if at_refs[1] == '':
                sla = default_sla
            else:
                sla = model.Sla.by_display_name(at_refs[1])
            if sla is None:
                raise ValueError("Bad default SLA name \"{}\" for AttributeType {}.".format(at_refs[1], at_name))
            if at_refs[2] == '':
                gt = default_gt
            else:
                gt = model.GraphType.by_display_name(at_refs[2])
            if gt is None:
                raise ValueError("Bad default GraphType name \"{}\" for AttributeType {}.".format(at_refs[2], at_name))
            
            model.DBSession.query(model.AttributeType).\
                    filter(model.AttributeType.display_name == at_name).\
                    update(
                        {'default_poller_set_id': ps.id,
                         'default_sla_id': sla.id,
                        # 'default_graph_type_id': gt.id
                        })

    def create_autodiscovery(self):
        for row in database_data.autodiscovery_policies:
            p = model.AutodiscoveryPolicy()
            (p.display_name,p.set_poller,p.permit_add,p.permit_delete,
                    p.alert_delete,p.permit_modify,p.permit_disable,
                    p.skip_loopback,p.check_state,p.check_address)=row
            model.DBSession.add(p)

    def create_backends(self):
        for row in database_data.backends:
            be = model.Backend()
            (be.display_name, be.command, be.parameters) = row
            if be.command == 'event':
                parms = be.parameters.split(',')
                event_type = model.EventType.by_tag(parms[0])
                if event_type is None:
                    raise ValueError("EventType {0} not found in backend {1}".format(parms[0], be.display_name))
                self.used_event_types.append(event_type.id)
            model.DBSession.add(be)

    def create_config_transfers(self):
        for row in database_data.config_transfers:
            ct = model.ConfigTransfer(row[0], row[1])
            model.DBSession.add(ct)

    def create_event_types(self):
        for row in database_data.event_types:
            et = model.EventType()
            try:
                (et.display_name, et.tag, et.text, et.generate_alarm, et.alarm_duration, et.show_host) = row
            except ValueError as errmsg:
                print("Bad event_type \"{0}\".\n{1}".format(row, errmsg))
                exit()
            model.DBSession.add(et)

    def create_graph_types(self):
        for atype_name,graphs in database_data.graph_types:
            attribute_type = model.AttributeType.by_display_name(atype_name)
            if attribute_type is None:
                raise ValueError(
                    "Attribute Type {} not found in GraphType".\
                    format(atype_name))
            for graph in graphs:
                gt = model.GraphType()
                try:
                    (gt.display_name, gt.vertical_label, gt.template,
                     gt.extra_options, graph_lines) = graph
                except ValueError as errmsg:
                    raise ValueError('{}\nRow:{}'.format(errmsg, graph))
                gt.attribute_type_id = attribute_type.id
                position=0
                for graph_line in graph_lines:
                    gl = model.GraphTypeLine()
                    try:
                        (rrd_name, gl.multiplier, gl.legend, gl.legend_unit) = graph_line
                    except ValueError as errmsg:
                        raise ValueError(
                            '{}: Bad Graphline in graph type {}'.\
                            format(errmsg, graph_line))
                    gl.attribute_type_rrd = model.AttributeTypeRRD.by_name(
                        attribute_type.id, rrd_name)
                    if gl.attribute_type_rrd is None:
                        raise ValueError('Bad RRD name {} in line {}'.format(
                            rrd_name, graph_line))
                    gl.position = position
                    gt.lines.append(gl)
                    position += 1
                model.DBSession.add(gt)

    def create_pollers(self):
        for row in database_data.pollers:
            p = model.Poller()
            (p.field, dn, p.command, p.parameters) = row
            p.display_name = unicode(dn)
            model.DBSession.add(p)

    def create_poller_sets(self):
        no_backend = model.Backend.by_display_name(u'No Backend')
        for row in database_data.poller_sets:
            (ps_name, at_name, poller_rows) = row
            atype = model.AttributeType.by_display_name(at_name)
            if atype is None:
                raise ValueError("Attribute type {0} not found.".format(at_name))
            ps = model.PollerSet(ps_name)
            ps.attribute_type = atype
            poller_row_pos = 0
            for poller_row in poller_rows:
                pr = model.PollerRow()
                pr.poller = model.Poller.by_display_name(poller_row[0])
                if pr.poller is None:
                    raise ValueError("Bad poller name \"{0}\".".format(poller_row[0]))
                if poller_row[1] == u'':
                    pr.backend = no_backend
                else:
                    pr.backend = model.Backend.by_display_name(poller_row[1])
                    if pr.backend is None:
                        raise ValueError("Bad backend name \"{0}\".".format(poller_row[1]))
                pr.position = poller_row_pos
                poller_row_pos += 1
                ps.poller_rows.append(pr)
            model.DBSession.add(ps)

    def create_severities(self):
        for severity in database_data.severities:
            sv = model.Severity(severity[0],severity[1],severity[2])
            model.DBSession.add(sv)

    def create_logmatches(self):
        logmatch_set = model.LogmatchSet(display_name=u'Default')
        model.DBSession.add(logmatch_set)

        for row in database_data.logfiles:
            lf = model.Logfile(row[0],row[1])
            lf.logmatchset = logmatch_set
            model.DBSession.add(lf)

        for row in database_data.logmatch_default_rows:
            lmr = model.LogmatchRow()
            try:
                (lmr.match_text, lmr.match_start, lmr.host_match, 
                    lmr.attribute_match, lmr.state_match, event_tag,
                    fields) = row
            except Exception as errmsg:
                raise ValueError("Cannot add row \"%s\": %s.\n" % (row[0], errmsg))
            else:
                lmr.event_type = model.EventType.by_tag(event_tag)
                if lmr.event_type is None:
                    raise ValueError("Bad EventType tag \"{}\" in LogMatchRow {}".format(event_tag, lmr.match_text))
                self.used_event_types.append(lmr.event_type.id)
                try:
                  lmr.match_sre = re.compile(row[0])
                except re.error as errmsg:
                    raise re.error("Cannot compile message \"%s\": %s" % (row[0],errmsg))
                lmr.logmatch_set = logmatch_set
                if fields is not None:
                    for field in fields:
                        lmf = model.LogmatchField()
                        try:
                            (lmf.event_field_tag, lmf.field_match)=field
                        except ValueError:
                            raise ValueError(
                                "Bad Field \"{}\" in LogMatchRow {}".format(
                                    field, lmr.match_text))
                        lmr.fields.append(lmf)
                model.DBSession.add(lmr)

    def create_slas(self):
        for row in database_data.slas:
            s = model.Sla()
            (s.display_name, s.event_text, attribute_type, sla_rows) = row
            s.attribute_type = model.AttributeType.by_display_name(attribute_type)
            if s.attribute_type is None:
                raise ValueError("Bad AttributeType name \"{}\" in SLA {}".format(attribute_type, s.display_name))
            model.DBSession.add(s)
            position=1
            for sla_row in sla_rows:
                sr = model.SlaRow(s,position=position)
                (sr.expression, sr.oper, sr.limit, sr.show_result, sr.show_info, sr.show_expression, sr.show_unit) = sla_row
                position += 1
                model.DBSession.add(sr)

    def create_snmp_communities(self):
        for row in database_data.snmp_communities:
            c = model.SnmpCommunity()
            (c.display_name, c.readonly, c.readwrite, c.trap) = row
            model.DBSession.add(c)

    def create_triggers(self):
        for trigger in database_data.triggers:
            t = model.Trigger()
            (t.display_name, t.email_owner, t.email_users, t.subject, t.body,
             rules) = trigger
            for rule in rules:
                r = model.TriggerRule()
                (field, r.oper, limits, r.stop, r.and_rule) = rule
                r.set_field(field)
                r.set_limit(limits)
                t.append(r)
            model.DBSession.add(t)
