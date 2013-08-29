

# Turbogears imports
from tg import expose, url
from tg.decorators import with_trailing_slash
from tgext.crud.decorators import optional_paginate

from tgext.admin.config import AdminConfig, CrudRestControllerConfig
from tgext.crud.controller import CrudRestController
from tgext.crud.utils import SortableTableBase, RequestLocalTableFiller

# third party imports

from rnms.lib.states import state_name
from rnms.lib.table import jqGridTableBase, jqGridTableFiller
from rnms.lib import admin_structures as st

class MyCrudRestController(CrudRestController):
    @with_trailing_slash
    @expose('mako:rnms.templates.admin.get_all')
    @expose('json:')
    @optional_paginate('value_list')
    def get_all(self, *args, **kw):
        return super(MyCrudRestController, self).get_all(*args, **kw)

class MyCrudRestControllerConfig(CrudRestControllerConfig):
    defaultCrudRestController = MyCrudRestController

class MyAdminConfig(AdminConfig):
    default_index_template = 'mako:rnms.templates.admin_top'
#    include_left_menu = False

    class attribute(MyCrudRestControllerConfig):
        class table_type(st.attribute, jqGridTableBase):
            __url__ = '/admin/attributes.json'
            pass
        class table_filler_type(st.attribute, jqGridTableFiller):
            pass

    class attributetype(MyCrudRestControllerConfig):
        class table_type(st.attribute_type, SortableTableBase):
            __xml_fields__ = ('default_poller_set')

        class table_filler_type(st.attribute_type, RequestLocalTableFiller):
            def default_poller_set(self, obj):
                return '<a href="{}/{}/edit">{}</a>'.format(
                        url('/admin/pollersets'),
                        obj.default_poller_set_id,
                        obj.default_poller_set.display_name)

    class autodiscoverypolicy(MyCrudRestControllerConfig):
        class table_type(st.autodiscovery_policy, SortableTableBase):
            pass
        class table_filler_type(st.autodiscovery_policy, RequestLocalTableFiller):
            pass
    
    class backend(MyCrudRestControllerConfig):
        class table_type(st.backend, SortableTableBase):
            pass
        class table_filler_type(st.backend, RequestLocalTableFiller):
            pass
    
    class eventstate(MyCrudRestControllerConfig):
        class table_type(st.event_state, SortableTableBase):
            __id__ = 'event_state-table'
            __column_widths__ = { 'id': 30,}
        class table_filler_type(st.event_state, RequestLocalTableFiller):
            def internal_state(self, obj):
                return state_name(obj.internal_state).capitalize()

    class eventtype(MyCrudRestControllerConfig):
        class table_type(st.event_type, SortableTableBase):
            __id__ = 'event_type-table'
            __column_widths__ = { 'id': 30, 'display_name': 250}
        class table_filler_type(st.event_type, RequestLocalTableFiller):
            pass
    class group(MyCrudRestControllerConfig):
        class table_type(st.group, SortableTableBase):
            __id__ = 'group-table'
            __column_widths__ = { 'group_id': 30, 'display_name': 250}
        class table_filler_type(st.group, RequestLocalTableFiller):
            pass

    class host(MyCrudRestControllerConfig):
        class table_type(st.host, SortableTableBase):
            __id__ = 'host-table'
            __column_widths__ = { 'id': 20,}
        class table_filler_type(st.host, RequestLocalTableFiller):
            pass

    class poller(MyCrudRestControllerConfig):
        class table_type(st.poller, SortableTableBase):
            pass
        class table_filler_type(st.poller, RequestLocalTableFiller):
            pass

    class pollerset(MyCrudRestControllerConfig):
        class table_type(st.poller_set, SortableTableBase):
            __id__ = 'poller_set-table'
        class table_filler_type(st.poller_set, RequestLocalTableFiller):
            def attribute_type(self, obj):
                return '<a href="{}/{}/edit">{}</a>'.format(
                        url('/admin/attributetypes'),
                        obj.attribute_type_id,
                        obj.attribute_type.display_name)

    class severity(MyCrudRestControllerConfig):
        class table_type(st.severity, SortableTableBase):
            __id__ = 'severity-table'
            __column_widths__ = { 'id': 30}
        class table_filler_type(st.severity, RequestLocalTableFiller):
            def fgcolor(self, obj):
                return '<div style="color: #{0}; background-color: #{1};">{0}</div>'.format(obj.fgcolor, obj.bgcolor)
    class user(MyCrudRestControllerConfig):
        class table_type(st.user, SortableTableBase):
            __id__ = 'user-table'
            __column_widths__ = { 'user_id': 30, 'created': 150}
        class table_filler_type(st.user, RequestLocalTableFiller):
            pass

    class zone(MyCrudRestControllerConfig):
        class table_type(st.zone, SortableTableBase):
            __id__ = 'zone-table'
            __column_widths__ = { 'id': 20,}
        class table_filler_type(st.zone, RequestLocalTableFiller):
            pass
