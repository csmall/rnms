

# Turbogears imports
from tg import expose, url
from tgext.admin.config import AdminConfig, CrudRestControllerConfig
from tgext.crud.controller import CrudRestController

# third party imports

from rnms.lib.states import state_name
from rnms.lib.table import jqGridTableBase, jqGridTableFiller
from rnms.lib import admin_structures as st

class MyCrudRestController(CrudRestController):
    keep_params = ['h']

    @expose('json')
    @expose('mako:rnms.templates.admin_view')
    def get_all(self, *args, **kw):
        return super(MyCrudRestController, self).get_all(*args, **kw)

class MyCrudRestControllerConfig(CrudRestControllerConfig):
    defaultCrudRestController = MyCrudRestController

class MyAdminConfig(AdminConfig):
    default_index_template = 'mako:rnms.templates.admin_top'
    #include_left_menu = False

    class attribute(MyCrudRestControllerConfig):
        class table_type(st.attribute, jqGridTableBase):
            __id__ = 'attribute-table'
            __column_widths__ = { 'id': 30,}
        class table_filler_type(st.attribute, jqGridTableFiller):
            def admin_state(self, obj):
                return state_name(obj.admin_state)

            def oper_state(self, obj):
                return 'hello'#state_name(obj.oper_state)
    
    class attributetype(MyCrudRestControllerConfig):
        class table_type(st.attribute_type, jqGridTableBase):
            __id__ = 'attribute_type-table'
            __column_widths__ = { 'id': 30,}
        class table_filler_type(st.attribute_type, jqGridTableFiller):
            def default_poller_set(self, obj):
                return '<a href="{}/{}/edit">{}</a>'.format(
                        url('/admin/pollersets'),
                        obj.default_poller_set_id,
                        obj.default_poller_set.display_name)

    class backend(MyCrudRestControllerConfig):
        class table_type(st.backend, jqGridTableBase):
            pass
        class table_filler_type(st.backend, jqGridTableFiller):
            pass
    
    class eventstate(MyCrudRestControllerConfig):
        class table_type(st.event_state, jqGridTableBase):
            __id__ = 'event_state-table'
            __column_widths__ = { 'id': 30,}
        class table_filler_type(st.event_state, jqGridTableFiller):
            def internal_state(self, obj):
                return state_name(obj.internal_state).capitalize()

    class eventtype(MyCrudRestControllerConfig):
        class table_type(st.event_type, jqGridTableBase):
            __id__ = 'event_type-table'
            __column_widths__ = { 'id': 30, 'display_name': 250}
        class table_filler_type(st.event_type, jqGridTableFiller):
            pass
    class group(MyCrudRestControllerConfig):
        class table_type(st.group, jqGridTableBase):
            __id__ = 'group-table'
            __column_widths__ = { 'group_id': 30, 'display_name': 250}
        class table_filler_type(st.group, jqGridTableFiller):
            pass

    class host(MyCrudRestControllerConfig):
        class table_type(st.host, jqGridTableBase):
            __id__ = 'host-table'
            __column_widths__ = { 'id': 20,}
        class table_filler_type(st.host, jqGridTableFiller):
            pass

    class poller(MyCrudRestControllerConfig):
        class table_type(st.poller, jqGridTableBase):
            pass
        class table_filler_type(st.poller, jqGridTableFiller):
            pass

    class pollerset(MyCrudRestControllerConfig):
        class table_type(st.poller_set, jqGridTableBase):
            __id__ = 'poller_set-table'
        class table_filler_type(st.poller_set, jqGridTableFiller):
            def attribute_type(self, obj):
                return '<a href="{}/{}/edit">{}</a>'.format(
                        url('/admin/attributetypes'),
                        obj.attribute_type_id,
                        obj.attribute_type.display_name)

    class severity(MyCrudRestControllerConfig):
        class table_type(st.severity, jqGridTableBase):
            __id__ = 'severity-table'
            __column_widths__ = { 'id': 30}
        class table_filler_type(st.severity, jqGridTableFiller):
            def fgcolor(self, obj):
                return '<div style="color: #{0}; background-color: #{1};">{0}</div>'.format(obj.fgcolor, obj.bgcolor)
    class user(MyCrudRestControllerConfig):
        class table_type(st.user, jqGridTableBase):
            __id__ = 'user-table'
            __column_widths__ = { 'user_id': 30, 'created': 150}
        class table_filler_type(st.user, jqGridTableFiller):
            pass

    class zone(MyCrudRestControllerConfig):
        class table_type(st.zone, jqGridTableBase):
            __id__ = 'zone-table'
            __column_widths__ = { 'id': 20,}
        class table_filler_type(st.zone, jqGridTableFiller):
            pass
