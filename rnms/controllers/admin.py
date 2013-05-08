

# Turbogears imports
from tg import expose
from tgext.admin.config import AdminConfig, CrudRestControllerConfig
from tgext.crud.controller import CrudRestController

# third party imports

from rnms.model import Attribute
from rnms.lib.states import state_name
from rnms.lib.table import jqGridTableBase, jqGridTableFiller

class MyCrudRestController(CrudRestController):

    @expose('json')
    @expose('mako:rnms.templates.get_all')
    def get_all(self, *args, **kw):
        return super(MyCrudRestController, self).get_all(*args, **kw)

class MyCrudRestControllerConfig(CrudRestControllerConfig):
    defaultCrudRestController = MyCrudRestController

class MyAdminConfig(AdminConfig):
    default_index_template = 'mako:rnms.templates.myadmintemplate'
    include_left_menu = False

    class attribute(MyCrudRestControllerConfig):
        menu_items = {}

        class table_type(jqGridTableBase):
            __entity__ = Attribute
            __id__ = 'attribute-table'
            __limit_fields__ = ('id', 'display_name', 'host')
            __headers__ = { 'id': 'ID',
                'display_name': 'Name', 'host': 'Host',
                'attribute_type': 'Attribute Type',
                'admin_state': 'Admin State', 
                'user': 'Owner',
            }
            __column_widths__ = {'id': '15',}


        class table_filler_type(jqGridTableFiller):
            __entity__ = Attribute
            __limit_fields__ = ('id', 'host', 'display_name', 'attribute_type',
                               'user','created')

            def admin_state(self, obj):
                print 'admin state'
                return state_name(obj.admin_state)

            def oper_state(self, obj):
                return 'hello'#state_name(obj.oper_state)

