
#from formencode import validators

# Turbogears imports
#from sprox.fillerbase import TableFiller
from tg import expose
from tg.decorators import with_trailing_slash, paginate
from tgext.admin.config import AdminConfig, CrudRestControllerConfig
from tgext.admin import AdminController
from tgext.crud.controller import CrudRestController
from sprox.tablebase import TableBase
#from tg.predicates import has_permission
#from tg import expose, validate

# third party imports
#from tg.i18n import lazy_ugettext as l_
#from sprox.tablebase import TableBase
from tw2.jqplugins.jqgrid import jqGridWidget
from tw2.core import Param

from rnms.model import Attribute
from rnms.lib.states import state_name
from rnms.lib.table import jqGridTableBase, jqGridTableFiller
#from tw2.forms import DataGrid

class MyCrudRestController(CrudRestController):
    def __init__(self, *args, **kw):
        print 'MyCRC init'
        super(MyCrudRestController, self).__init__(*args, **kw)


class MyCrudRestControllerConfig(CrudRestControllerConfig):
    defaultCrudRestController = MyCrudRestController

class MyAdminConfig(AdminConfig):
    default_index_template = 'mako:rnms.templates.myadmintemplate'
    include_left_menu = False

    class attribute(CrudRestControllerConfig):
        menu_items = {}

        class table_type(jqGridTableBase):
            __entity__ = Attribute
            __id__ = 'attribute-table'
            __limit_fields__ = ('display_name', 'host')
            __headers__ = { 'id': 'ID',
                'display_name': 'Name', 'host': 'Host',
                'attribute_type': 'Attribute Type',
                'admin_state': 'Admin State', 
                'user': 'Owner',
            }


        class table_filler_type(jqGridTableFiller):
            __entity__ = Attribute
            __limit_fields__ = ('id', 'display_name', 'host', 'attribute_type',
                               'user','created')

            def admin_state(self, obj):
                print 'admin state'
                return state_name(obj.admin_state)

            def oper_state(self, obj):
                return 'hello'#state_name(obj.oper_state)

class TestWidget(jqGridWidget):
    id='testw'
    xml_fields = Param('xml_fields', attribute=False)
    fields = Param('fields', default=[], attribute=False)
    columns = Param('fields', default=[], attribute=False)
    pager_options = { "search" : True, "refresh" : True, "add" : False, }

    def __init__(self, action, attrs, value):
        #print 'init action', action
        #print 'init attrs', attrs
        #print 'init value', value
        #print 'init arfgs', args #emty
        #print 'init kw', kw['value']
        #print 'init vtype', type(kw['value'])

        #    pass#print 'v',v
        self.options = {
            'pager': 'test',
            #'data': [{'foo':'1', 'bar':'2'}, {'foo': 'a', 'bar':'b'}],
            'colModel': [{'name':f[0],} for f in self.fields],
            'datatype': 'local',
            'height': 'auto',
            'rowNum': value.item_count,
            #'page': value.page,
        }
        data = []
        for v in value.items:
            data.append({field[0]:field[1](v) for field in self.fields})
        self.options['data'] = data
        #self.options['data'] = [v for v in value]#[ {'host':v['host'], 'display_name':v['display_name']} for v in value]
        #print  [f for  f in self.fields]
        #print self.fields[0][1]

        super(TestWidget, self).__init__()


    def prepare(self):
        print 'preppks', self.pks
        super(TestWidget, self).prepare()

#class TestTableBase(TableBase):
#    __base_widget_type__ = TestWidget
#
#    def _do_get_widget_args(self):
#        args = super(TestTableBase, self)._do_get_widget_args()
#        #print 'do get widget args', args
#        args['foo'] = 'bar'
#        return args
#
#class AdminController2(AdminController):
#    """ The new admin controller """
#    allow_only = has_permission('manage',
#                                msg=l_('Only for users with manage permission'))
#
#    @expose('rnms.templates.testindex')
#    def index(self):
#        """ Top-level page of the new administration """
#        return dict(page='some_where')
#    
#    @expose('rnms.templates.testindex')
#    @validate(validators={'model_name':validators.String()})
#    def _default(self, model_name, objid=None, **kw):
#        """Let the user know that this action is protected too."""
#        model_name = model_name[:-1]
#        print self.config.models[model_name]
#        
#        return dict(page='some_where')
