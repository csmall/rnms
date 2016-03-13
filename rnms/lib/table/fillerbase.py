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

import operator
from tg import url

from sprox.fillerbase import TableFiller, FillerBase
from sqlalchemy import and_, desc, not_
from sqlalchemy.orm import RelationshipProperty

from rnms.model import AttributeType

from column_operators import COL_OPERATORS


class jqGridTableFiller(TableFiller):
    __possible_field_names__ = ['display_name']
    __hide_primary_field__ = False

    def _calculate_pages(self, total_rows, **kw):
        try:
            limit = int(kw['rows'])
        except:
            limit = None
        current_page = kw.pop('page', 1)
        if limit is None or limit < 1:
            total_pages = 1
        else:
            total_pages = total_rows / limit + 1
        return current_page, total_pages

    def _get_rows(self, items):
        """ Convert the items into rows that jqGrid understands """
        identifier = self.__provider__.get_primary_field(self.__entity__)
        if self.__hide_primary_field__:
            suppress_id = identifier
        else:
            suppress_id = ''

        rows = []
        for item in items:
            try:
                rows.append({f: item[f] for f in self.__fields__
                             if f != suppress_id})
            except IndexError:
                pass
        return rows

    def _do_search_conditions(self, query, _search, **kw):
        """ Add additional filter objects if we are being called with
        search options """
        if not _search:
            return query
        try:
            search_field = kw['searchField']
            search_string = kw['searchString']
            search_oper = kw['searchOper']
        except KeyError:
            return query

        op, do_not = self._get_search_op(search_oper)
        if op is None:
            return query.filter('0=1')
        if self.is_relation(search_field):
            # I'll fix this one day when i understand inspect()
            try:
                field = getattr(self.__entity__, search_field+'_id')
            except AttributeError:
                return query.filter('0=1')
        else:
            try:
                field = getattr(self.__entity__, search_field)
            except AttributeError:
                return query.filter('0=1')

        if do_not:
            return query.filter(not_(op(field, search_string)))
        return query.filter(op(field, search_string))

    def _extra_filters(self, **kw):
        """ Extra filtering due to the url we are passed, generally it
        limits the child items (these object) down to a given parent ID
        """
        filters = (  # get var, db foreign key id
            ('a', 'attribute_id'),
            ('at', 'attribute_type_id'),
            ('gt', 'graph_type_id'),
            ('h', 'host_id'),
            ('ps', 'poller_set_id'),
            ('z', 'zone_id'),
        )
        conditions = []

        for id_letter, col_name in filters:
            try:
                parent_id = int(kw[id_letter])
                parent_col = getattr(self.__entity__, col_name)
            except:  # Dont care why we fail, we'll skip it
                continue
            else:
                conditions.append(parent_col == parent_id)
        return conditions

    def _do_get_provider_count_and_objs(self, _search=False,  **kw):
        limit = kw.pop('rows', None)
        page = kw.pop('page', 1)
        sidx = kw.pop('sidx', '')
        sord = kw.pop('sord', 'asc')
        kw.pop('nd', False)
        sort_desc = (sord == 'desc')
        if limit is None or page < 1:
            offset = 0
        else:
            try:
                offset = int(page-1) * int(limit)
            except TypeError:
                offset = 0
        # Extra filters
        conditions = self._extra_filters(**kw)

        count, objs = self._do_query(limit, offset, sidx, sort_desc,
                                     conditions, _search, **kw)
        self.__count__ = count
        return count, objs

    def _do_sorting(self, query, sort_idx, sort_desc):
        """ Set the sorting on the query based upon the sort
        index (the fieldname) and the sort order """
        if hasattr(self.__entity__, sort_idx):
            try:
                sort_table =\
                    self.__entity__.__mapper__.relationships[sort_idx]
                sort_field = sort_table.table.c['display_name']
                query = query.join(sort_table.table)
            except KeyError:
                try:
                    sort_field =\
                        self.__entity__.__mapper__.c[sort_idx]
                except KeyError:
                    return query
            if sort_desc:
                return query.order_by(desc(sort_field))
            else:
                return query.order_by(sort_field)
        return query

    def get_value(self, value=None, **kw):
        items = super(jqGridTableFiller, self).get_value(value, **kw)
        total_records = self.__count__
        current_page, total_pages = self._calculate_pages(total_records, **kw)
        rows = self._get_rows(items)
        return dict(total=total_pages, page=current_page,
                    entries=rows)

    def _get_columns(self):
        """ Return a list of columns given the entity and the relations """
        tables = [self.__entity__]
        columns = []
        for f in self.__fields__:
            if f in self.__entity__.__mapper__.c:
                columns.append(self.__entity__.__mapper__.c[f])
            else:
                try:
                    fkey_table = self.__entity__.__mapper__.\
                        relationships[f].table
                except KeyError:
                    continue
                if fkey_table not in tables:
                    tables.append(fkey_table)
                columns.append(fkey_table.c['display_name'])
        return tables, columns

    def _do_query(self, limit, offset, sort_idx, sort_desc, conditions,
                  _search, **kw):
        """
        Query the database, this is based upon the sprox sa_provider
        query method but is better as its filtering does a lot more
        """
        query = self.__provider__.session.query(self.__entity__).\
            filter(and_(*conditions))
        query = self._do_search_conditions(query, _search, **kw)
        count = query.count()

        # sorting
        if sort_idx != '':
            query = self._do_sorting(query, sort_idx, sort_desc)

        if offset is not None:
            query = query.offset(offset)
        if limit is not None:
            query = query.limit(limit)

        objs = query.all()
        return count, objs

    def is_relation(self, field_name):
        """ Return True if field_name is a relation for __entity__ """
        return isinstance(
            self.__entity__.__mapper__.get_property(field_name),
            RelationshipProperty)

    def _get_search_op(self, search_oper):
        """ Translate the search_oper string into a real operator """
        try:
            return COL_OPERATORS[search_oper]
        except KeyError:
            pass
        try:
            return getattr(operator, search_oper), False
        except:
            pass
        return None, False


class DiscoveryFiller(FillerBase):

    def get_value(self, value=None, **kw):
        from rnms.model.host import Host
        from rnms.lib.discovery.attributes import DiscoverHostAttributes

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
                if hasattr(att, 'id'):
                    action = '<a href="{}">Edit</a>'.format(
                        url('/admin/attributes/'+str(att.id)))
                else:
                    action = 'Add'
                    row_id = '{}-{}'.format(atype_id, idx)
                rows.append({
                    'action': action,
                    'display_name': att.display_name,
                    'admin_state': att.admin_state,
                    'oper_state': att.oper_state,
                    'attribute_type': atype_name,
                    })
        return {'totals': len(rows), 'rows': rows}
