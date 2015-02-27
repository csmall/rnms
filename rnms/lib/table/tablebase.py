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

from sprox.tablebase import TableBase
from tw2.jqplugins.jqgrid import jqGridWidget
import tw2.core as twc

from column_operators import COL_OPERATORS

SEARCH_OPTIONS = [x for x in COL_OPERATORS.keys()]


class jqGridGrid(jqGridWidget):
    """
    Standard jQuery UI grid for the TableBase
    """
    id = None
    url = None
    url_args = None
    columns = None
    suppress_id = None
    caption = None
    scroll = False
    height = None
    default_sort = None
    default_sort_order = None
    toolbar_items = ''

    params = ('id', 'scroll', 'height', 'caption', 'columns',
              'column_widths', 'default_column_width', 'url_args',
              'default_sort', 'default_sort_order')
    options = {
        'altRows': False,
#        'altclass': 'altrows',
        'datatype': 'json',
        'autowidth': True,
        'toolbar': (True, 'top'),
        #'imgpath': 'scripts/jqGrid/themes/green/images',
        'jsonReader': {
            'repeatitems': False,
            'id': 0,
            'root': 'value_list.entries',
            'total': 'value_list.total',
            'page': 'value_list.page',
        },
        'loadComplete': twc.js_symbol('console.debug($(".delete-confirm"))'),
    }
    pager_options = {"search": True, "refresh": True, "edit": False,
                     "del": False, "add": False}

    def __init__(self, action=None, postdata=None):
        if postdata is not None and postdata != {}:
            self.options['postData'] = postdata
        else:
            self.options['postData'] = {}

        if self.url_args is None:
            self.url_args = {}
        super(jqGridGrid, self).__init__()

        if action is not None:
            self.options['url'] = action
        else:
            self.options['url'] = url(self.url, self.url_args)
        self.options['caption'] = self.caption
        self.options['colNames'] = self._get_colnames()
        self.options['colModel'] = self._get_colmodel()
        self.options['scroll'] = self.scroll
        if not self.scroll:
            self.options['pager'] = self.id+'-pager'
        self.options['height'] = self.height

        if self.default_sort is not None:
            self.options['sortname'] = self.default_sort
        if self.default_sort_order is not None:
            self.options['sortorder'] = self.default_sort_order

        # If we are using actions then ID is second column
        # otherwise we get <tr id="action stuff"...
        if self.columns[0] == '__actions__':
            self.options['jsonReader']['id'] = 1

    def _get_colnames(self):
        colnames = []
        for col in self.columns:
            if col == self.suppress_id:
                continue
            try:
                colnames.append(self.headers[col])
            except KeyError:
                colnames.append(
                    ' '.join(w.capitalize() for w in col.split('_')))
        return colnames

    def _get_colmodel(self):
        colmodel = []
        default_width = self.default_column_width
        for colname in self.columns:
            if colname == self.suppress_id:
                continue
            try:
                width = self.column_widths[colname]
            except KeyError:
                width = default_width

            col_def = self._get_search(colname)
            col_def.update({
                'name': colname,
                'index': colname,
                'width': width})

            colmodel.append(col_def)
        return colmodel

    def _get_search(self, colname):
        """ Create the colmodel search items for the given colname
        this is a dict that is placed into the columns colmodel """

        if colname == 'display_name':
            return {
                'stype': 'text',
                'searchoptions': {
                    'sopt': SEARCH_OPTIONS,
                },
            }
        if colname == 'host' and 'h' not in self.url_args:
            try:
                data_url = url('/hosts/option', {'z': self.url_args['z']})
            except KeyError:
                data_url = url('/hosts/option')
            return {
                'stype': 'select',
                'searchoptions': {
                    'dataUrl': data_url,
                    'sopt': ['eq', 'ne'],
                }
            }
        if colname == 'attribute' and 'a' not in self.url_args:
            try:
                data_url = url('/attributes/option', {'h': self.url_args['h']})
            except KeyError:
                data_url = url('/attributes/option')
            return {
                'stype': 'select',
                'searchoptions': {
                    'dataUrl': data_url,
                    'sopt': ['eq', 'ne'],
                }
            }
        if colname == 'created':
            return {
                'stype': 'text',
                'searchoptions': {
                    'dataInit':
                    'function(el){$(el).datepicker().change(function()'
                    '{$("#grid-id")[0].triggerToolbar();});};',
                    'attr': {'title': 'Select Date'}}
            }
        if colname == 'event_type':
            data_url = url('/events/type_option')
            return {
                'stype': 'select',
                'searchoptions': {
                    'dataUrl': data_url,
                    'sopt': ['eq', 'ne'],
                }
            }
        if colname == 'zone' and 'z' not in self.url_args:
            data_url = url('/zones/option')
            return {
                'stype': 'select',
                'searchoptions': {
                    'dataUrl': data_url,
                    'sopt': ['eq', 'ne'],
                }
            }
        return dict(search=False)


class jqGridTableBase(TableBase):
    """ A table widget using jqueryUI
    Modifiers:
        __headers__ dict of column field/header pairs
        __column_widths__  dict of column field/width pairs
        __default_column_width__  column width if not found above
    """
    __caption__ = None
    __base_widget_type__ = jqGridGrid
    __url__ = None
    __retrieves_own_value__ = True
    __default_column_width__ = 100
    __hide_primary_field__ = False
    __scroll__ = False
    __height__ = 'auto'
    __default_sort__ = 'id'
    __default_sort_order__ = 'asc'

    def _do_get_widget_args(self):
        args = super(jqGridTableBase, self)._do_get_widget_args()
        if self.__url__ is not None:
            args['url'] = self.__url__
        if self.__caption__ is not None:
            args['caption'] = self.__caption__
        args['columns'] = self.__fields__
        args['headers'] = self.__headers__
        args['id'] = self.__grid_id__
        args['scroll'] = self.__scroll__
        args['height'] = self.__height__
        if self.__hide_primary_field__:
            args['suppress_id'] = \
                self.__provider__.get_primary_field(self.__entity__)
        if self.__default_sort__ is not None:
            args['default_sort'] = self.__default_sort__
        if self.__default_sort_order__ is not None:
            args['default_sort_order'] = self.__default_sort_order__
        return args
