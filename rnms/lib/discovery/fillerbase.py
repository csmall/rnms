# -*- coding: utf-8 -*-
#
# This file is part of the RoseNMS
#
# Copyright (C) 2012-2014 Craig Small <csmall@enc.com.au>
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

from tg import url

from sprox.fillerbase import FillerBase
from sqlalchemy import and_

from rnms.model import AttributeType, Attribute, DBSession, Host
from rnms.lib.discovery.attributes import DiscoverHostAttributes


class DiscoveryFiller(FillerBase):

    def get_value(self, value=None, **kw):

        host_id = kw.pop('h', None)
        if host_id is None:
            return {}
        host = Host.by_id(host_id)
        if host is None:
            return {}
        sd = DiscoverHostAttributes(host)
        sd.discover()
        rows = []
        for atype_id, atts in sd.combined_atts.items():
            atype_name = AttributeType.name_by_id(atype_id)
            for idx, att in atts.items():
                existing_att = DBSession.query(Attribute).filter(and_(
                    Attribute.host_id == host.id,
                    Attribute.attribute_type_id == atype_id,
                    Attribute.index == idx)).first()
                if existing_att:
                    action =\
                        '''<a href={}><button type="button" class="btn
                    btn-info btn-xs">Edit</button></a>'''.format(
                            url('/admin/attributes/{}/edit'.format(
                                existing_att.id)))
                else:
                    action = ''
                rows.append({
                    'action': action,
                    'id': idx,
                    'atype_id': atype_id,
                    'display_name': att.display_name,
                    'admin_state': att.admin_state,
                    'oper_state': att.oper_state,
                    'attribute_type': atype_name,
                    'fields': att.fields,
                    })
        return {'totals': len(rows), 'rows': rows}
