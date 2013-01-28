# -*- coding: utf-8 -*-
#
# This file is part of the Rosenberg NMS
#
# Copyright (C) 2013 Craig Small <csmall@enc.com.au>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <http://www.gnu.org/licenses/>
#
import logging
import datetime
import time
import asyncore
import transaction

from sqlalchemy import and_

from rnms import model

class RnmsInfo(object):
    """
    Provides information about the various objects in rnms
    """

    def _snmp_data(self,community):
        if community is None:
            return '(not set)'
        elif community[0] == '1':
            return 'SNMPv1 set'
        elif community[0] == '2':
            return 'SNMPv2c set'
        elif community[0] == '3':
            return 'SNMPv3 set'
        return 'unknown'
        
    def host_info(self, ids):
        hosts = model.DBSession.query(model.Host).filter(model.Host.id.in_(ids))
        if hosts.count() == 0:
            print "No hosts found"
            return
        print
        for host in hosts:
            print '=' * 60
            print '{:<20} | {}: {}'.format('Host', host.id, host.display_name)
            print '-' * 60
            print '''{:<20} | {}: {}
{:<20} | {}
{:<20} | {}
{:<20} | {}
{:<20} | {}
{:<20} | {} : {}
{:<20} | {}
{:<20} | {}
{:<20} | ({}) {}'''.format(
        'Zone', host.zone.id, host.zone.display_name,
        'Management IP', host.mgmt_address,
        'System ObjID', host.sysobjid,
        'SNMP RO', self._snmp_data(host.community_ro),
        'SNMP RW', self._snmp_data(host.community_rw),
        'Autodiscovery', host.autodiscovery_policy.id, host.autodiscovery_policy.display_name,
        'Created', host.created,
        'Polled', host.polled,
        'Attributes', len(host.attributes), ', '.join([str(a.id) for a in host.attributes])
        )

    def attribute_info(self, ids):
        attributes = model.DBSession.query(model.Attribute).filter(model.Attribute.id.in_(ids))
        if attributes.count() == 0:
            print "No attributes found"
            return
        print
        for attribute in attributes:
            print '=' * 60
            print '{:<20}| {}: {} (index: {})'.format('Attribute', attribute.id, attribute.display_name, attribute.index)
            print '-' * 60
            print """{:<20} | {}: {}
{:<20} | {}/{}
{:<20} | {}: {}
{:<20} | {}: {} (enabled:{})
{:<20} | {}: {}
{:<20} | {}
{:<20} | {}
{:<20} | {}""".format(
        'Host', attribute.host.id, attribute.host.display_name,
        'State (admin/oper)', attribute.admin_state_name(), attribute.oper_state_name(),
        'Attribute Type', attribute.attribute_type.id, attribute.attribute_type.display_name,
        'Poller Set', attribute.poller_set.id, attribute.poller_set.display_name, attribute.poll_enabled,
        'SLA', attribute.sla.id, attribute.sla.display_name,
        'Created', attribute.created,
        'Polled', attribute.polled,
        'Next Poll', attribute.next_poll)
            print '-' * 60
            print 'Fields'
            for field in attribute.fields:
                at_field = model.AttributeTypeField.by_id(field.attribute_type_field_id)
                print '{:<20} | {}'.format(at_field.display_name,field.value)

    def pollerset_info(self, ids):
        poller_sets = model.DBSession.query(model.PollerSet).filter(model.PollerSet.id.in_(ids))
        if poller_sets.count() == 0:
            print "No pollersets found"
            return
        print
        for poller_set in poller_sets:
            print '=' * 60
            print 'Poller Set          | {}: {}'.format(poller_set.id, poller_set.display_name)
            print '-' * 60
            print '''{:<20} | {}:{}
            '''.format(
                    'Attribute Type', poller_set.attribute_type_id, poller_set.attribute_type.display_name,
                    )
            print '-' * 60
            print 'Poller Rows\nPos| {:<39} | {:<29}'.format('Poller','Backend')
            for row in poller_set.poller_rows:
                print '{:<3}| {:<3}:{:<35} | {:<3}:{:<25}'.format(
                        row.position,
                        row.poller_id,
                        (row.poller.display_name+' ('+row.poller.command+')')[:35],
                        row.backend_id,
                        (row.backend.display_name+' ('+row.backend.command+')')[:25],
                        )

    def autodiscovery_info(self, ids):
        """ Information about the autodiscovery policy """
        policies = model.DBSession.query(model.AutodiscoveryPolicy).filter(model.AutodiscoveryPolicy.id.in_(ids))
        if policies.count() == 0:
            print "No Autodiscovery Policies found"
            return
        print
        for policy in policies:
            print '=' * 60
            print '{:<30} | {}: {}'.format('Autodiscovery Policy', policy.id, policy.display_name)
            print '-' * 60
            print '''Autodiscovery will not examine attribute if it:
{:<30} | {}
{:<30} | {}
{:<30} | {}

Attribute Autodiscovery can do the following:
{:<30} | {}
{:<30} | {}
{:<30} | {}
{:<30} | {}
{:<30} | {}
            '''.format(
                    ' - is a Loopback', policy.skip_loopback,
                    ' - is Oper Down', policy.check_state,
                    ' - has no address', policy.check_address,
                    ' - set the PollerSet', policy.set_poller,
                    ' - add new attributes', policy.permit_add,
                    ' - disable missing attributes', policy.permit_disable,
                    ' - delete missing attributes ', policy.permit_delete,
                    ' - alert on missing attributes', policy.alert_delete,
                    ' - modify attribute fields', policy.permit_modify,
                    )
    
    
    def _parse_sysobjid(self, sysobjid):
        if sysobjid is None or sysobjid == '':
            return 'No SNMP required'
        elif sysobjid == '.':
            return 'All SNMP enabled hosts'
        return 'sysObjectId='+ sysobjid

    def attributetype_info(self, ids):
        """ Information about the attribute types """
        atypes = model.DBSession.query(model.AttributeType).filter(model.AttributeType.id.in_(ids))
        if atypes.count() == 0:
            print "No AttributeTypes found"
            return
        print
        for atype in atypes:
            print '=' * 60
            print '{:<30} | {}: {}'.format('Attribute Type', atype.id, atype.display_name)
            print '-' * 60
            print '''{:<30} | (enabled: {})
{:<30} | {}
{:<30} | {}
{:<30} | {}({})
{:<30} | {}: {}
{:<30} | {}: {}
{:<30} | Heatbeat: {} CF: {} Rows: {}
'''.format(
        'Autodiscovery', atype.ad_enabled,
        'Required Host SNMP', self._parse_sysobjid(atype.required_sysobjid),
        'Validate', atype.ad_validate,
        'Command', atype.ad_command, atype.ad_parameters,
        'Default PollerSet', atype.default_poller_set_id, atype.default_poller_set.display_name,
        'Default SLA', atype.default_sla_id, atype.default_sla.display_name,
        'RRA Info', atype.ds_heartbeat, atype.rra_cf, atype.rra_rows,
        )
            print '-' * 60
            print 'Fields'
            for field in atype.fields:
                print '{:<3} {:<26} | tag:{}'.format(field.position, field.display_name, field.tag)
            
            print '-' * 60
            print 'RRDtool files'
            for rrd in atype.rrds:
                print '{:<3} {:<26} | {:<5} {}'.format(rrd.position, rrd.display_name, rrd.dst2str(), rrd.name)


    def trigger_info(self, ids):
        """ Information about the triggers """
        triggers = model.DBSession.query(model.Trigger).filter(model.Trigger.id.in_(ids))
        if triggers.count() == 0:
            print "No Triggers found"
            return
        print
        for trigger in triggers:
            print '=' * 60
            print '''{:<30} | {}: {}
{:<30} | {}
{:<30} | {} - {}'''.format('Trigger', trigger.id, trigger.display_name,
        'Match Type', trigger.match_type_name().capitalize(),
        'Email: Owner - Users', trigger.email_owner, trigger.email_users,
        )
            print '-' * 60
            print 'Rules'
            for rule in trigger.rules:
                stop = rule.stop and 'STOP' or 'CONTINUE'
                andor = rule.and_rule and 'AND' or 'OR'
                print '{}: {} {} {} ({} - {})'.format(
                        rule.position, rule.field_name(), rule.oper, rule.limit,andor, stop)
