

# Turbogears imports
from tg import expose
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
