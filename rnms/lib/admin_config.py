# -*- coding: utf-8 -*-
#
# This file is part of the RoseNMS
#
# Copyright (C) 2012-2016 Craig Small <csmall@enc.com.au>
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

# Turbogears imports
from tg import url

from tgext.admin.tgadminconfig import BootstrapTGAdminConfig
from tgext.admin.widgets import BootstrapAdminTableBase as TableBase,\
    BootstrapAdminEditableForm as EditableForm,\
    BootstrapAdminAddRecordForm as AddRecordForm
# from tgext.admin.widgets import BootstrapAdminTableFiller as TableFiller
from tgext.admin.layouts import BootstrapAdminLayout
from tgext.admin.config import CrudRestControllerConfig
from tgext.crud.controller import CrudRestController
from tg.predicates import has_permission

# third party imports

from rnms.lib import admin_tables as at
from rnms.lib.admin_tables import TableFiller, click
from rnms.model import ConfigBackupMethod
from rnms import model
from rnms.widgets.button import Button


class MyAdminLayout(BootstrapAdminLayout):
    crud_templates = {
        'get_all': ['mako:rnms.templates.admin.get_all', ],
        'edit': ['mako:rnms.templates.admin.edit', ],
        'new': ['mako:rnms.templates.admin.new', ],
        }


class MyCrudRestController(CrudRestController):
    title = 'RoseNMS Admin'
    allow_only = has_permission('manage')


class MyCrudRestControllerConfig(CrudRestControllerConfig):
    defaultCrudRestController = MyCrudRestController


class MyAdminConfig(BootstrapTGAdminConfig):
    # layout = MyAdminLayout
    include_left_menu = False

    class attribute(CrudRestControllerConfig):
        class table_type(at.attribute, TableBase):
            __xml_fields__ = ('host',)

        class table_filler_type(at.attribute, at.TableFiller):
            def extra_actions(self, obj):
                return Button(
                    url('/admin/attributefields/',
                        {'attribute_id': obj.id}),
                    'list', 'info',
                    tooltip='Show fields')

    class attributefield(MyCrudRestControllerConfig):
        class table_type(at.attribute_field, TableBase):
            __xml_fields__ = ('attribute',)
            __headers__ = {
                'id': 'ID', 'attribute': 'Attribute',
                'attribute_type_field': 'Field Name',
                'value': 'Field Value'
                }

        class table_filler_type(at.attribute_field, TableFiller):
            def attribute(self, obj):
                return click('attributes', obj.attribute_id,
                             obj.attribute.display_name)
            pass

    class attributetype(MyCrudRestControllerConfig):
        class table_type(at.attribute_type, TableBase):
            __xml_fields__ = ('default_poller_set')

        class table_filler_type(at.attribute_type, TableFiller):
            def extra_actions(self, obj):
                return Button(
                    url('/admin/attributetypefields',
                        {'attribute_type_id': obj.id}),
                    'list', 'info',
                    tooltip='Show Fields for this Attribute Type') +\
                    Button(
                    url('/admin/attributetyperrds',
                        {'attribute_type_id': obj.id}),
                    'signal', 'info',
                    tooltip='Show RRDs for this Attribute Type')

            def default_poller_set(self, obj):
                return '<a href="{}/{}/edit">{}</a>'.format(
                    url('/admin/pollersets'),
                    obj.default_poller_set_id,
                    obj.default_poller_set.display_name)

    class attributetyperrd(MyCrudRestControllerConfig):
        class table_type(at.attribute_type_rrd, TableBase):
            pass

        class table_filler_type(at.attribute_type_rrd, TableFiller):
            pass

    class autodiscoverypolicy(MyCrudRestControllerConfig):
        class table_type(at.autodiscovery_policy, TableBase):
            pass

        class table_filler_type(at.autodiscovery_policy, TableFiller):
            pass

    class backend(MyCrudRestControllerConfig):
        class table_type(at.backend, TableBase):
            pass

    class eventstate(MyCrudRestControllerConfig):
        class table_type(at.event_state, TableBase):
            pass

        class table_filler_type(at.event_state, TableFiller):
            def internal_state(self, obj):
                return 'FIXME!!'  # state_name(obj.internal_state).capitalize()

    class eventtype(MyCrudRestControllerConfig):
        class table_type(at.event_type, TableBase):
            __column_widths__ = {'id': 30, 'display_name': 250}

        class table_filler_type(at.event_type, TableFiller):
            pass

    class graphtype(MyCrudRestControllerConfig):
        class table_type(at.graph_type, TableBase):
            __column_widths__ = {'id': 20, 'display_name': 50}

        class table_filler_type(at.graph_type, TableFiller):
            def extra_actions(self, obj):
                return Button(url('/admin/graphtypelines/',
                                  {'graph_type_id': obj.id}),
                              'list', 'info',
                              tooltip='Show Lines') +\
                    Button(url('/admin/attributetyperrds/',
                               {'attribute_type_id': obj.attribute_type_id}),
                           'signal', 'info',
                           tooltip='Show RRDs')

    class graphtypeline(MyCrudRestControllerConfig):
        class table_type(at.graph_type_line, TableBase):
            pass

        class table_filler_type(at.graph_type_line, TableFiller):
            pass

    class group(MyCrudRestControllerConfig):
        class table_type(at.group, TableBase):
            __column_widths__ = {'group_id': 30, 'display_name': 250}

        class table_filler_type(at.group, TableFiller):
            pass

    class host(CrudRestControllerConfig):
        class new_form_type(AddRecordForm):
            __model__ = model.Host
            __limit_fields__ = [
                'id', 'mgmt_address', 'display_name', 'zone', 'tftp_server',
                'ro_community', 'rw_community', 'trap_community',
                'autodiscovery_policy', 'config_backup_method',
                ]

        class edit_form_type(EditableForm):
            __model__ = model.Host
            __limit_fields__ = [
                'id', 'mgmt_address', 'display_name', 'zone', 'tftp_server',
                'ro_community', 'rw_community', 'trap_community',
                'autodiscovery_policy', 'config_backup_method',
                ]

        class table_type(at.host, TableBase):
            __column_widths__ = {'id': 20}

        class table_filler_type(at.host, at.TableFiller):
            pass

    class logfile(MyCrudRestControllerConfig):
        class table_type(at.logfile, TableBase):
            pass

        class table_filler_type(at.logfile, TableFiller):
            pass

    class logmatchset(MyCrudRestControllerConfig):
        class table_type(at.logmatchset, TableBase):
            pass

        class table_filler_type(at.logmatchset, TableFiller):
            pass

    class logmatchrow(MyCrudRestControllerConfig):
        class table_type(at.logmatchrow, TableBase):
            pass

        class table_filler_type(at.logmatchrow, TableFiller):
            pass

    class permission(MyCrudRestControllerConfig):
        class table_type(at.permission, TableBase):
            pass

        class table_filler_type(at.permission, TableFiller):
            pass

    class poller(MyCrudRestControllerConfig):
        class table_type(at.poller, TableBase):
            pass

        class table_filler_type(at.poller, TableFiller):
            pass

    class pollerset(MyCrudRestControllerConfig):
        class table_type(at.poller_set, TableBase):
            __xml_fields__ = ('attribute_type',)

        class table_filler_type(at.poller_set, TableFiller):
            def extra_actions(self, obj):
                return Button(
                    url('/admin/pollerrows',
                        {'poller_set_id': obj.id}),
                    'list', 'info',
                    tooltip='Show rows for this Poller Set')

            def attribute_type(self, obj):
                return '<a href="{}/{}/edit">{}</a>'.format(
                    url('/admin/attributetypes'),
                    obj.attribute_type_id,
                    obj.attribute_type.display_name)

    class pollerrow(MyCrudRestControllerConfig):
        class table_type(at.poller_row, TableBase):
            __xml_fields__ = ('poller_set', 'poller', 'backend')

        class table_filler_type(at.poller_row, TableFiller):
            def poller_set(self, obj):
                return click('pollersets', obj.poller_set_id,
                             obj.poller_set.display_name)

            def poller(self, obj):
                return click('pollers', obj.poller_id,
                             obj.poller.display_name)

            def backend(self, obj):
                return click('backends', obj.backend_id,
                             obj.backend.display_name)

    class severity(MyCrudRestControllerConfig):
        class table_type(at.severity, TableBase):
            __column_widths__ = {'id': 30}

        class table_filler_type(at.severity, TableFiller):
            def fgcolor(self, obj):
                return '<div style="color: #{0}; background-color: #{1};">' + \
                    '{0}</div>'.format(obj.fgcolor, obj.bgcolor)

    class snmpdevice(MyCrudRestControllerConfig):
        class table_type(at.snmp_device, TableBase):
            pass

        class table_filler_type(at.snmp_device, TableFiller):
            def oid(self, obj):
                return 'ent.{}.{}{}'.format(
                    obj.enterprise_id, 'X.' * obj.enterprise.device_offset,
                    obj.oid)

    class snmpenterprise(MyCrudRestControllerConfig):
        class table_type(at.snmp_enterprise, TableBase):
            pass

        class table_filler_type(at.snmp_enterprise, TableFiller):
            pass

    class trigger(MyCrudRestControllerConfig):
        class table_type(at.trigger, TableBase):
            __headers__ = {'id': 'ID', 'display_name': 'Trigger Name',
                           'email_owner': 'Email Owner',
                           'email_users': 'Email Users',
                           }

        class table_filler_type(at.trigger, TableFiller):
            pass

    class user(MyCrudRestControllerConfig):
        class table_type(at.user, TableBase):
            __headers__ = {
                'user_id': 'ID', 'display_name': 'Name',
                'user_name': 'Username', 'created': 'Created'}

        class table_filler_type(at.user, TableFiller):
            def groups(self, obj):
                if len(obj.groups) == 0:
                    return ''
                return ''.join(
                    ['<a href="{}">{}</a>'.format(
                        url('/admin/groups/{}/edit'.format(g.group_id)),
                        g.group_name)
                        for g in obj.groups])

    class zone(MyCrudRestControllerConfig):
        class table_type(at.zone, TableBase):
            pass

        class table_filler_type(at.zone, TableFiller):
            pass

    class configbackupmethod(MyCrudRestControllerConfig):

        class table_type(TableBase):
            __entity__ = ConfigBackupMethod
            __headers__ = {
                'id': 'ID',
                'display_name': 'Backup Method',
                'plugin_name': 'Plugin',
                }
