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


def make_attribute_command(command, parameters):
    class AttributeCommand(object):
        """ Class that contains all attribute commands """
        _command = None
        _parameters = None

        def __init__(self, command, parameters):
            self._command = getattr(self, 'run_'+command, None)
            self._parameters = parameters

        def run(self, host, trap):
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
                if varbind.oid == self.attribute_parameters:
                    return (DBSession.query(Attribute).filter(and_(
                        Attribute.host_id == host.id,
                        Attribute.attribute_type_id == self.attribute_type_id,
                        Attribute.index == varbind.value
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
                Attribute.attribute_type_id == self.attribute_type_id,
                )).first(), None)
            return (None, None)

    cmd = AttributeCommand(command, parameters)
    return cmd.run


def make_value_command(command, parameters):
    class ValueCommand(object):
        """ Class that contains all value commands """
        _command = None
        _parameters = None

        def __init__(self, command, parameters):
            self._command = getattr(self, 'run_'+command, None)
            self.parameters = parameters

        def run(self, host, trap):
            if self._command is None:
                return (None, None)
            return self._command(host, trap)

        ### Real run commands go here
        def _run_oid(self, host, trap):
            """
            Parameters: <oid>|<val1>=<ret1>,...|<default ret>
            oid   = The OID of varbind holding the state
            <val> = Mapping of OID result. If <state> is <val1> then return
                      <ret1> - optional
            <default ret> If state is OID no match of previous field - otional
            """
            params = self.parmeters('|')

            state_oid = params[0]

            for varbind in trap.varbinds:
                if varbind.oid == state_oid:
                    if len(params) == 1:
                        return (varbind.value, None)

                    for item in params[1].split(','):
                        try:
                            (match, ret) = item.split('=')
                        except ValueError:
                            pass
                        else:
                            if varbind.value == match:
                                return (ret, None)
                    else:
                        try:
                            return (params[2], None)
                        except IndexError:
                            pass
            return (None, None)

        def _run_fixed(self, host, trap):
            """ The value is fixed in the parameters """
            return (self.value_parameters, None)


class MatchTrap(object):
    """ Static object for SNMP Trap matches """
    __copy_attrs__ = (
        'stop_if_match',
        )

    def __init__(self, db_match):
        self._attribute_command = make_attribute_command(
            db_match.attribute_command,
            db_match.attribute_parameters)
        self._value_command = make_value_command(
            db_match.attribute_command,
            db_match.attribute_parameters)
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

        value, error = self._value_command(host, trap)
        if error is not None:
            return (None, None, error)
        return (attribute, value, None)
