
from tgext.admin.config import AdminConfig, CrudRestControllerConfig
from sprox.tablebase import TableBase
from sprox.fillerbase import TableFiller

from rnms.model import Attribute
from rnms.lib.states import state_name

class MyAdminConfig(AdminConfig):
    default_index_template = 'mako:rnms.templates.myadmintemplate'
    include_left_menu = False

    class attribute(CrudRestControllerConfig):
        menu_items = {}
        class table_type(TableBase):
            __entity__ = Attribute
            __headers__ = { 'id': 'ID',
                'display_name': 'Name', 'host': 'Host',
                'attribute_type': 'Attribute Type',
                'admin_state': 'Admin State', 'oper_state': 'Oper State',
                'user': 'Owner',
            }
            __omit_fields__ = (
                'host_id', 'attribute_type_id', 'sla_id', 'poller_set_id',
                'user_id', 'poll_priority', 'poll_interval',
                'events', 'alarms', 'fields', 'index', 'make_sound',)
            __field_order__ = [
                'id', 'display_name', 'host', 'attribute_type', 'user', 
                'admin_state',
                'oper_state', 'poller_set', 'sla', 'created']

        class table_filler_type(TableFiller):
            __entity__ = Attribute
            __omit_fields__ = ('events', 'alarms', 'fields')
            def admin_state(self, obj):
                return state_name(obj.admin_state)

            def oper_state(self, obj):
                return state_name(obj.oper_state)


