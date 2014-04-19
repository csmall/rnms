# -*- coding: utf-8 -*-
#
# This file is part of the Rosenberg NMS
#
# Copyright (C) 2013-2014 Craig Small <csmall@enc.com.au>
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
from sqlalchemy import and_

from rnms.model import DBSession, Attribute
from rnms.lib.backend import CacheBackend


def make_attribute_command(db_match):
    class AttributeCommand(object):
        """ Class that contains all attribute commands """
        _command = None
        _parameters = None
        _attribute_type_id = None

        def __init__(self, db_match):
            self._command = getattr(self, '_run_'+db_match.attribute_command)
            self._parameters = db_match.attribute_parameters
            self._attribute_type_id = db_match.attribute_type_id

        def run(self, host, trap):
            print self._command
            if self._command is None:
                return (None, None)
            return self._command(host, trap)

        ### Real run commands go here
        def _run_match_index(self, host, trap):
            """
            Match the ID of one of the VarBinds to an Attribute's index field
            and pass back the state. The only Attributes searched in the host
            must have the same AttributeID as the Trap.

            Parameters: <index_oid>
              index_oid = The OID of the VarBind that holds the index
            """
            for varbind in trap.varbinds:
                if varbind.oid.startswith(self._parameters):
                    return (DBSession.query(Attribute).filter(and_(
                        Attribute.host_id == host.id,
                        Attribute.attribute_type_id == self._attribute_type_id,
                        Attribute.index == str(varbind.value)
                        )).first(), None)
            return (None, None)

        def _run_first(self, host, trap):
            """
            Return the first Attribute for given host that has the
            required AttributeType. Used for where the Attribute doesn't
            matter OR there is only one of this AttributeType per host.
            Parameters: ignored
            """
            return (DBSession.query(Attribute).filter(and_(
                Attribute.host_id == host.id,
                Attribute.attribute_type_id == self._attribute_type_id,
                )).first(), None)
            return (None, None)

    cmd = AttributeCommand(db_match)
    return cmd.run


def make_value_command(command, parameters):
    class ValueCommand(object):
        """ Class that contains all value commands """
        _command = None
        _parameters = None

        def __init__(self, command, parameters):
            self._command = getattr(self, '_run_'+command, None)
            self._parameters = parameters

        def run(self, host, trap):
            if self._command is None:
                return (None, None)
            return self._command(host, trap)

        ### Real run commands go here
        def _run_dict(self, host, trap):
            """
            Return a dictionary of values obtained from the varbinds
            Parameters: <key1>=<oid1>,<key2>=<oid2>,...
            <keyX> = key for the returned dictionary
            <oidX> = oid of varbind to use for value
            """
            values = {}
            for params in self._parameters.split(','):
                try:
                    key, match_oid = params.split('=')
                except ValueError:
                    continue
                for varbind in trap.varbinds:
                    if varbind.oid.startswith(match_oid):
                        values[key] = varbind.value
                        break
                else:
                    values[key] = None
            return values, None

        def _run_oid(self, host, trap):
            """
            Find the given OID and return its value
            Parameters: <oid>|<default>
            <oid> = OID of varbind to return
            <default> = Optional default value if not found
            """
            params = self._parameters.split('|')
            if len(params) == 2:
                default = params[1]
            else:
                default = None
            for varbind in trap.varbinds:
                if varbind.oid.startswith(params[0]):
                    return varbind.value, None
            return default, None

        def _run_oid_map(self, host, trap):
            """
            Parameters: <oid>|<val1>=<ret1>,...|<default ret>
            oid   = The OID of varbind holding the state
            <val> = Mapping of OID result. If <state> is <val1> then return
                      <ret1> - optional
            <default ret> If state is OID no match of previous field - otional
            """
            params = self._parameters.split('|')
            if len(params) < 2:
                return None, 'Need at least 2 parameters'
            match_oid = params[0]
            mappings = params[1]
            try:
                default = params[2]
            except IndexError:
                default = None

            for varbind in trap.varbinds:
                if varbind.oid.startswith(match_oid):
                    for mapping in mappings.split(','):
                        try:
                            match, value = mapping.split('=')
                        except ValueError:
                            return None, 'Mapping is wrong for'.format(mapping)
                        if varbind.value == match:
                            return value, None
            return default, None

        def _run_fixed(self, host, trap):
            """ The value is fixed in the parameters """
            return (self._parameters, None)
    cmd = ValueCommand(command, parameters)
    return cmd.run


class MatchTrap(object):
    """ Static object for SNMP Trap matches """
    __copy_attrs__ = (
        'stop_if_match',
        )

    def __init__(self, db_match):
        self._attribute_command = make_attribute_command(db_match)
        self._value_commands = {
            v.key: make_value_command(v.command, v.parameters)
            for v in db_match.values}
        self.backend = CacheBackend(db_match.backend)
        for copy_attr in self.__copy_attrs__:
            setattr(self, copy_attr, getattr(db_match, copy_attr))

    def run(self, host, trap):
        """
        Further matching of the trap.  At this point the consolidator
        has found a host that matches the agent's address and a trap_oid
        for this match.

        This method looks at the trap varbinds and attempts to locate
        an attribute of the host plus some optional results.
        The attribute and results will be fed into a backend.
        Returns:
          (attribute, result, error)
            attribute is a matched attribute for this trap. If returns
            None it means there is no match
            result is similiar to a poller result
        """
        attribute, error = self._attribute_command(host, trap)
        if error is not None:
            return (None, None, error)
        elif attribute is None:
            return (None, None, None)

        error = None
        return_values = {}
        for k, value_command in self._value_commands.items():
            value, error = value_command(host, trap)
            if error is not None:
                return (None, None, error)
            return_values[k] = value
        return (attribute, return_values, None)
