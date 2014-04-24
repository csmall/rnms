

# Turbogears imports
from tg import url

from tgext.admin.tgadminconfig import BootstrapTGAdminConfig
from tgext.admin.config import CrudRestControllerConfig
from tgext.crud.controller import CrudRestController

# third party imports

from rnms.lib.states import state_name
from rnms.lib import admin_tables as at
from rnms.model import ConfigBackupMethod

from sprox.tablebase import TableBase
from sprox.fillerbase import FillerBase


class MyCrudRestController(CrudRestController):
    #pagination_enabled = False
    title = 'Rosenberg NMS Admin'


class MyCrudRestControllerConfig(CrudRestControllerConfig):
    defaultCrudRestController = MyCrudRestController


class MyAdminConfig(BootstrapTGAdminConfig):
    #default_index_template = 'mako:rnms.templates.admin_top'
    #include_left_menu = False

    class attribute(MyCrudRestControllerConfig):
        class table_type(at.attribute, TableBase):
            __xml_fields__ = ('host',)

        class table_filler_type(at.attribute, at.TableFiller):
            pass

    class attributetype(MyCrudRestControllerConfig):
        class table_type(at.attribute_type, TableBase):
            pass

        class table_filler_type(at.attribute_type, at.TableFiller):
            def default_poller_set(self, obj):
                return '<a href="{}/{}/edit">{}</a>'.format(
                    url('/admin/pollersets'),
                    obj.default_poller_set_id,
                    obj.default_poller_set.display_name)

    class attributetyperrd(MyCrudRestControllerConfig):
        class table_type(at.attribute_type_rrd, TableBase):
            pass

        class table_filler_type(at.attribute_type_rrd, FillerBase):
            pass

    class autodiscoverypolicy(MyCrudRestControllerConfig):
        class table_type(at.autodiscovery_policy, TableBase):
            pass

        class table_filler_type(at.autodiscovery_policy, FillerBase):
            pass

    class backend(MyCrudRestControllerConfig):
        class table_type(at.backend, TableBase):
            pass

        class table_filler_type(at.backend, FillerBase):
            pass

    class eventstate(MyCrudRestControllerConfig):
        class table_type(at.event_state, TableBase):
            pass

        class table_filler_type(at.event_state, FillerBase):
            def internal_state(self, obj):
                return state_name(obj.internal_state).capitalize()

    class eventtype(MyCrudRestControllerConfig):
        class table_type(at.event_type, TableBase):
            __column_widths__ = {'id': 30, 'display_name': 250}

        class table_filler_type(at.event_type, FillerBase):
            pass

    class graphtype(MyCrudRestControllerConfig):
        class table_type(at.graph_type, TableBase):
            __column_widths__ = {'id': 20, 'display_name': 50}

        class table_filler_type(at.graph_type, FillerBase):
            pass

    class graphtypeline(MyCrudRestControllerConfig):
        class table_type(at.graph_type_line, TableBase):
            pass

        class table_filler_type(at.graph_type_line, FillerBase):
            pass

    class group(MyCrudRestControllerConfig):
        class table_type(at.group, TableBase):
            __column_widths__ = {'group_id': 30, 'display_name': 250}

        class table_filler_type(at.group, FillerBase):
            pass

    class host(MyCrudRestControllerConfig):
        class table_type(at.host, TableBase):
            __column_widths__ = {'id': 20}

        class table_filler_type(at.host, at.TableFiller):
            pass

    class logfile(MyCrudRestControllerConfig):
        class table_type(at.logfile, TableBase):
            pass

        class table_filler_type(at.logfile, FillerBase):
            pass

    class logmatchset(MyCrudRestControllerConfig):
        class table_type(at.logmatchset, TableBase):
            pass

        class table_filler_type(at.logmatchset, FillerBase):
            pass

    class logmatchrow(MyCrudRestControllerConfig):
        class table_type(at.logmatchrow, TableBase):
            pass

        class table_filler_type(at.logmatchrow, FillerBase):
            pass

    class poller(MyCrudRestControllerConfig):
        class table_type(at.poller, TableBase):
            pass

        class table_filler_type(at.poller, FillerBase):
            pass

    class pollerset(MyCrudRestControllerConfig):
        class table_type(at.poller_set, TableBase):
            pass

        class table_filler_type(at.poller_set, FillerBase):
            def attribute_type(self, obj):
                return '<a href="{}/{}/edit">{}</a>'.format(
                    url('/admin/attributetypes'),
                    obj.attribute_type_id,
                    obj.attribute_type.display_name)

    class pollerrow(MyCrudRestControllerConfig):
        class table_type(at.poller_row, TableBase):
            pass

        class table_filler_type(at.poller_row, FillerBase):
            pass

    class severity(MyCrudRestControllerConfig):
        class table_type(at.severity, TableBase):
            __column_widths__ = {'id': 30}

        class table_filler_type(at.severity, FillerBase):
            def fgcolor(self, obj):
                return '<div style="color: #{0}; background-color: #{1};">' + \
                    '{0}</div>'.format(obj.fgcolor, obj.bgcolor)

    class user(MyCrudRestControllerConfig):
        class table_type(at.user, TableBase):
            __column_widths__ = {'user_id': 30, 'created': 150}

        class table_filler_type(at.user, FillerBase):
            pass

    class zone(MyCrudRestControllerConfig):
        class table_type(at.zone, TableBase):
            pass

        class table_filler_type(at.zone, FillerBase):
            pass

    class configbackupmethod(MyCrudRestControllerConfig):

        class table_type(TableBase):
            __entity__ = ConfigBackupMethod
            __headers__ = {
                'id': 'ID',
                'display_name': 'Backup Method',
                'plugin_name': 'Plugin',
                }
