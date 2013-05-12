

# Turbogears imports
from tg import expose
from tgext.admin.config import AdminConfig, CrudRestControllerConfig
from tgext.crud.controller import CrudRestController

# third party imports

from rnms.lib.states import state_name
from rnms.lib.table import jqGridTableBase, jqGridTableFiller
from rnms.lib import structures as st

class MyCrudRestController(CrudRestController):
    keep_params = ['h']

    @expose('json')
    @expose('mako:rnms.templates.get_all')
    def get_all(self, *args, **kw):
        return super(MyCrudRestController, self).get_all(*args, **kw)

class MyCrudRestControllerConfig(CrudRestControllerConfig):
    defaultCrudRestController = MyCrudRestController

class MyAdminConfig(AdminConfig):
    default_index_template = 'mako:rnms.templates.myadmintemplate'
    #include_left_menu = False

    class attribute(MyCrudRestControllerConfig):
        class table_type(st.attribute, jqGridTableBase):
            __id__ = 'attribute-table'
            __column_widths__ = {'id': '15',}
        class table_filler_type(st.attribute, jqGridTableFiller):
            def admin_state(self, obj):
                print 'admin state'
                return state_name(obj.admin_state)

            def oper_state(self, obj):
                return 'hello'#state_name(obj.oper_state)

    class host(MyCrudRestControllerConfig):
        class table_type(st.host, jqGridTableBase):
            __id__ = 'host-table'
            __column_widths__ = {'id': '15',}
        class table_filler_type(st.host, jqGridTableFiller):
            def __actions__(self, obj):
                value  = super(jqGridTableFiller, self).__actions__(obj)
                value +=\
     '<div><a href="/admin/attributes?h={}">Show Attributes</a></div>'.format(
         obj.id)
                return value
    
    class zone(MyCrudRestControllerConfig):
        class table_type(st.zone, jqGridTableBase):
            __id__ = 'zone-table'
            __column_widths__ = {'id': '15',}
        class table_filler_type(st.zone, jqGridTableFiller):
            pass
