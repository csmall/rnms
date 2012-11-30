# -*- coding: utf-8 -*-
#
# This file is part of the Rosenberg NMS
#
# Copyright (C) 2001 Craig Small <csmall@enc.com.au>
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
""" Auto-discovery Policy """

from sqlalchemy import Column
from sqlalchemy.types import Integer, Boolean, Unicode
#from sqlalchemy.orm import relation, backref

from rnms.model import DeclarativeBase
from rnms.lib import snmp


class AutodiscoveryPolicy(DeclarativeBase):
    __tablename__ = 'autodiscovery_policies'
    
    #{ Columns
    
    id = Column(Integer, primary_key=True)
    display_name=Column(Unicode(40), unique=True)
    set_poller = Column(Boolean,default=True)
    permit_add = Column(Boolean,default=False)
    permit_delete = Column(Boolean,default=False)
    alert_delete = Column(Boolean,default=True)
    permit_modify = Column(Boolean,default=False)
    permit_disable = Column(Boolean,default=False)
    skip_loopback = Column(Boolean,default=False)
    check_state = Column(Boolean,default=True)
    check_address = Column(Boolean,default=True)
    
    #}
    def __init__(self,display_name=None):
        self.display_name = display_name
        self.set_poller = 0
        self.permit_add = 0
        self.permit_delete = 0
        self.alert_delete = 0
        self.permit_modify = 0
        self.permit_disable = 0
        self.skip_loopback = 0
        self.check_state = 0
        self.check_address = 0

    def can_add(self, new_attribute):
        """
        Does this policy permit the new attribute 'new_attribute' to
        be added?
        """
        if new_attribute.attribute_type is None:
            print("no attr typ")
            return False
        if new_attribute.attribute_type.ad_validate == False:
            return True

        ipaddr = new_attribute.get_field('address')

        # Policy doesnt permit loopback interfaces to be added
        if self.skip_loopback == True and ipaddr == '127.0.0.1':
            return False

        # Policy does not permit attributes with no addresses to be added
        if self.check_address == True and ipaddr in (None,  u'', u'0.0.0.0'):
            return False

        # Policy does not permit attributes that are not up to be added
        if self.check_state == 1 and new_attribute.oper_state != snmp.STATE_UP:
            return False

        return True

    def can_del(self):
        """
        Does this policy permit the deletion of a missing attribute?
        """
        return (self.permit_delete and not self.permit_disable)

    def can_disable(self):
        """
        Does this policy permit the setting of an attribute polling to 
        disabled
        """
        return (not self.permit_delete and self.permit_disable)

