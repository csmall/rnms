# -*- coding: utf-8 -*-
#
# This file is part of the RoseNMS
#
# Copyright (C) 2014-2015 Craig Small <csmall@enc.com.au>
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
from cliff.lister import Lister
from sqlalchemy import and_
from rnms import model


class List(Lister):
    """ List items within the RNMS database """

    def get_parser(self, prog_name):
        query_types = list(x[:-5] for x in dir(self) if x[-5:] == '_info')
        parser = super(List, self).get_parser(prog_name)
        parser.add_argument(
            action='store',
            dest='qtype',
            type=str,
            choices=query_types,
            help='Query Type:' + ', '.join(query_types),
            metavar='['+'|'.join(query_types)+']')
        parser.add_argument(
            '-H', '--host',
            action='store',
            dest='hosts',
            type=str,
            help='Limit listing to given host IDs',
            metavar='HID,...'
            )
        parser.add_argument(
            '-t', '--atype',
            action='store',
            dest='atypes',
            type=str,
            help='Listing to given Attribute Type IDs',
            metavar='ID,...'
            )
        parser.add_argument(
            '-Z', '--zone',
            action='store',
            dest='zones',
            type=str,
            help='Limit listing to given zone IDs',
            metavar='ID,...'
            )
        return parser

    def take_action(self, parsed_args):
        try:
            real_info = getattr(self, parsed_args.qtype+'_info')
        except AttributeError:
            raise RuntimeError(
                'Unknown query type "{}".'.format(parsed_args.qtype))
        return real_info(parsed_args)

    def _create_conditions(self, parsed_args, valid_conditions):
        """ Create a list of conditions with the given parsed_args
        """
        for (arg_key, field) in valid_conditions:
            conditions = []
            values = getattr(parsed_args, arg_key)
            if values is None:
                continue
            conditions.append(field.in_(values.split(',')))
        return conditions

    def attributes_info(self, parsed_args):
        conditions = self._create_conditions(
            parsed_args, (
                ('hosts', model.Attribute.host_id),
                ('atypes', model.Attribute.attribute_type_id),
                ))
        attributes = model.DBSession.query(model.Attribute).\
            join(model.Host).\
            join(model.AttributeType).\
            filter(and_(*conditions)).\
            order_by(model.Attribute.id)
        return(
            ('ID', 'Name', 'Host', 'HID', 'Type', 'TID',),
            ((
                a.id, a.display_name,
                a.host.display_name, a.host_id,
                a.attribute_type.display_name,
                a.attribute_type_id,
                )for a in attributes)
        )

    def attributetypes_info(self, parsed_args):
        conditions = []
        attribute_types = model.DBSession.query(model.AttributeType).\
            filter(and_(*conditions)).\
            order_by(model.AttributeType.id)
        return(
            ('ID', 'Name', 'Command'),
            ((
                a.id, a.display_name,
                a.ad_command,
                )for a in attribute_types)
        )

    def hosts_info(self, parsed_args):
        conditions = self._create_conditions(
            parsed_args, (
                ('zones', model.Zone.id),))
        hosts = model.DBSession.query(model.Host).\
            join(model.Zone).\
            filter(and_(*conditions)).\
            order_by(model.Host.id)
        return(
            ('ID', 'Name', 'Zone', 'ZID', ),
            ((
                h.id, h.display_name, h.zone.display_name, h.zone_id,
            ) for h in hosts)
        )
