

# Turbogears imports
from tg import expose, url, request, tmpl_context
from tg.decorators import with_trailing_slash

from tgext.admin.config import AdminConfig, CrudRestControllerConfig
from tgext.crud.controller import CrudRestController

# third party imports

from rnms.lib.states import state_name
from rnms.lib.table import jqGridTableBase, jqGridTableFiller
from rnms.lib import admin_structures as st


class MyCrudRestController(CrudRestController):
    pagination_enabled = False

    @with_trailing_slash
    @expose('mako:rnms.templates.admin.get_all')
    @expose('json:')
    def get_all(self, *args, **kw):
        if request.response_type == 'application/json':
            values = self.table_filler.get_value(*args, **kw)
            return dict(value_list=values)
        postdata = {}
        for key in ('a','h', 'ps', 'z'):
            if key in kw:
                postdata[key] = kw[key]

        tmpl_context.widget = self.table
        return dict(model=self.model.__name__, griddata=postdata)
    @expose()
    def foof(self, *args, **kw):
        print 'fffooo'
        return 'fggfdgfgfdg'

class MyCrudRestControllerConfig(CrudRestControllerConfig):
    defaultCrudRestController = MyCrudRestController

class MyAdminConfig(AdminConfig):
    default_index_template = 'mako:rnms.templates.admin_top'
#    include_left_menu = False

    class attribute(MyCrudRestControllerConfig):
        class table_type(st.attribute, jqGridTableBase):
            pass
        class table_filler_type(st.attribute, jqGridTableFiller):
            pass

    class attributetype(MyCrudRestControllerConfig):
        class table_type(st.attribute_type, jqGridTableBase):
            pass
        class table_filler_type(st.attribute_type, jqGridTableFiller):
            def default_poller_set(self, obj):
                return '<a href="{}/{}/edit">{}</a>'.format(
                        url('/admin/pollersets'),
                        obj.default_poller_set_id,
                        obj.default_poller_set.display_name)

    class autodiscoverypolicy(MyCrudRestControllerConfig):
        class table_type(st.autodiscovery_policy, jqGridTableBase):
            pass
        class table_filler_type(st.autodiscovery_policy, jqGridTableFiller):
            pass
    
    class backend(MyCrudRestControllerConfig):
        class table_type(st.backend, jqGridTableBase):
            pass
        class table_filler_type(st.backend, jqGridTableFiller):
            pass
    
    class eventstate(MyCrudRestControllerConfig):
        class table_type(st.event_state, jqGridTableBase):
            pass
        class table_filler_type(st.event_state, jqGridTableFiller):
            def internal_state(self, obj):
                return state_name(obj.internal_state).capitalize()

    class eventtype(MyCrudRestControllerConfig):
        class table_type(st.event_type, jqGridTableBase):
            __column_widths__ = { 'id': 30, 'display_name': 250}
        class table_filler_type(st.event_type, jqGridTableFiller):
            pass

    class group(MyCrudRestControllerConfig):
        class table_type(st.group, jqGridTableBase):
            __column_widths__ = { 'group_id': 30, 'display_name': 250}
        class table_filler_type(st.group, jqGridTableFiller):
            pass

    class host(MyCrudRestControllerConfig):
        class table_type(st.host, jqGridTableBase):
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
            pass
        class table_filler_type(st.poller_set, jqGridTableFiller):
            def attribute_type(self, obj):
                return '<a href="{}/{}/edit">{}</a>'.format(
                        url('/admin/attributetypes'),
                        obj.attribute_type_id,
                        obj.attribute_type.display_name)

    class pollerrow(MyCrudRestControllerConfig):
        class table_type(st.poller_row, jqGridTableBase):
            pass
        class table_filler_type(st.poller_row, jqGridTableFiller):
            pass

    class severity(MyCrudRestControllerConfig):
        class table_type(st.severity, jqGridTableBase):
            __column_widths__ = { 'id': 30}
        class table_filler_type(st.severity, jqGridTableFiller):
            def fgcolor(self, obj):
                return '<div style="color: #{0}; background-color: #{1};">{0}</div>'.format(obj.fgcolor, obj.bgcolor)
    
    class user(MyCrudRestControllerConfig):
        class table_type(st.user, jqGridTableBase):
            __column_widths__ = { 'user_id': 30, 'created': 150}
        class table_filler_type(st.user, jqGridTableFiller):
            pass

    class zone(MyCrudRestControllerConfig):
        class table_type(st.zone, jqGridTableBase):
            __column_widths__ = { 'id': 20,}
        class table_filler_type(st.zone, jqGridTableFiller):
            pass
