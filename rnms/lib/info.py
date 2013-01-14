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

    def host_info(self, ids):
        hosts = model.DBSession.query(model.Host).filter(model.Host.id.in_(ids))
        if hosts.count() == 0:
            print "No hosts found"
            return
        print
        for host in hosts:
            print '=' * 60
            print 'Host          | {}: {}'.format(host.id, host.display_name)
            print '-' * 60
            print 'Zone          | {}: {}'.format(host.zone.id, host.zone.display_name)
            print 'Management IP | {}'.format(host.mgmt_address)
            print 'System ObjID  | {}'.format(host.sysobjid)
            print 'Autodiscovery | {}: {}'.format(host.autodiscovery_policy.id, host.autodiscovery_policy.display_name)
            print 'Created       | {}'.format(host.created)
            print 'Polled        | {}'.format(host.polled)
            print 'Attributes    | ({}) '.format(len(host.attributes)) +', '.join([str(a.id) for a in host.attributes])

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
{:<20} | {}
{:<20} | {}
{:<20} | {}""".format(
        'Host', attribute.host.id, attribute.host.display_name,
        'State (admin/oper)', attribute.admin_state_name(), attribute.oper_state_name(),
        'Attribute Type', attribute.attribute_type.id, attribute.attribute_type.display_name,
        'Poller Set', attribute.poller_set.id, attribute.poller_set.display_name, attribute.poll_enabled,
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
