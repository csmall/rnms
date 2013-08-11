
import operator

from sprox.tablebase import TableBase
from sprox.fillerbase import TableFiller, FillerBase
from tg import url
from sqlalchemy import and_, desc, not_
from sqlalchemy.orm import RelationshipProperty
from sqlalchemy.sql.operators import ColumnOperators as coop

from tw2.jqplugins.jqgrid import jqGridWidget

from rnms.model import AttributeType

COL_OPERATORS = {
    'eq':   (coop.__eq__, False),
    'ne':   (coop.__ne__, False),
    'bw':   (coop.startswith, False),
    'bn':   (coop.startswith, True),
    'ew':   (coop.endswith, False),
    'en':   (coop.endswith, True),
    'cn':   (coop.contains, False),
    'nc':   (coop.contains, True),
}
SEARCH_OPTIONS = [x for x in COL_OPERATORS.keys()]

class jqGridGrid(jqGridWidget):
    """
    Standard jQuery UI grid for the TableBase
    """
    id = None
    url = None
    url_args = None
    columns = None
    suppress_id = None
    caption = None
    scroll = False
    height = None

    params = ['id', 'scroll', 'height', 'caption', 'columns',
              'column_widths', 'default_column_width', 'url_args',]
    options = {
        'datatype': 'json',
        'autowidth': True,
        'imgpath': 'scripts/jqGrid/themes/green/images',
        'jsonReader' : {
            'repeatitems': False,
            'id': 0,
        },
    }
    pager_options = { "search" : True, "refresh" : True, "edit" : False,
                     "del" : False, "add" : False}
    def __init__(self, action=None):
        #self.url_args = {}
        super(jqGridGrid, self).__init__()
        if action is not None:
            self.options['url'] = action
        else:
            self.options['url'] = url(self.url,self.url_args)
        self.options['caption'] = self.caption
        self.options['colNames'] = self._get_colnames()
        self.options['colModel'] = self._get_colmodel()
        self.options['scroll'] = self.scroll
        if self.scroll == False:
            self.options['pager'] = self.id+'-pager'
        self.options['height'] = self.height

    def _get_colnames(self):
        colnames = []
        for col in self.columns:
            if col== self.suppress_id:
                continue
            try:
                colnames.append(self.headers[col])
            except KeyError:
                colnames.append(col.capitalize())
        return colnames

    def _get_colmodel(self):
        colmodel  = []
        default_width =  self.default_column_width
        for colname in self.columns:
            if colname == self.suppress_id:
                continue
            try:
                width = self.column_widths[colname]
            except KeyError:
                width = default_width

            col_def = self._get_search(colname)
            col_def.update({
                'name': colname,
                'index': colname,
                'width': width})

            colmodel.append(col_def)
        return colmodel

    def _get_search(self, colname):
        """ Create the colmodel search items for the given colname
        this is a dict that is placed into the columns colmodel """

        if colname == 'display_name':
            return {
                'stype': 'text',
                'searchoptions': {
                    'sopt': SEARCH_OPTIONS,
                },
            }
        if colname == 'host' and 'h' not in self.url_args:
            try:
                data_url = url('/hosts/option', {'z':self.url_args['z']})
            except KeyError:
                data_url = url('/hosts/option')
            return {
                'stype': 'select',
                'searchoptions': {
                    'dataUrl': data_url,
                    'sopt': ['eq', 'ne'],
                }
            }
        if colname == 'attribute' and 'a' not in self.url_args:
            try:
                data_url = url('/attributes/option', {'h':self.url_args['h']})
            except KeyError:
                data_url = url('/attributes/option')
            return {
                'stype': 'select',
                'searchoptions': {
                    'dataUrl': data_url,
                    'sopt': ['eq', 'ne'],
                }
            }
        if colname == 'created':
            return {
                'stype': 'text',
                'searchoptions': {
                    'dataInit':
                    'function(el){$(el).datepicker().change(function(){$("#grid-id")[0].triggerToolbar();});};',
                    'attr': {'title': 'Select Date'}}
            }
        if colname == 'event_type':
            data_url = url('/events/type_option')
            return {
                'stype': 'select',
                'searchoptions': {
                    'dataUrl': data_url,
                    'sopt': ['eq', 'ne'],
                }
            }
        if colname == 'zone' and 'z' not in self.url_args:
            data_url = url('/zones/option')
            return {
                'stype': 'select',
                'searchoptions': {
                    'dataUrl': data_url,
                    'sopt': ['eq', 'ne'],
                }
            }
        return dict(search=False)

class jqGridTableBase(TableBase):
    """ A table widget using jqueryUI
    Modifiers:
        __headers__ dict of column field/header pairs
        __column_widths__  dict of column field/width pairs
        __default_column_width__  column width if not found above
    """
    __caption__ = None
    __base_widget_type__ = jqGridGrid
    __url__ = None
    __retrieves_own_value__ = True
    __default_column_width__ = 100
    __hide_primary_field__ = False
    __scroll__ = False
    __height__ = 'auto'

    def _do_get_url_args(self):
        try:
            if self.attribute_id is not None:
                return dict(a=self.attribute_id)
        except AttributeError:
            pass
        try:
            if self.host_id is not None:
                return dict(h=self.host_id)
        except AttributeError:
            pass
        return {}

    def _do_get_widget_args(self):
        args = super(jqGridTableBase, self)._do_get_widget_args()
        if self.__url__ is not None:
            args['url'] = self.__url__
            args['url_args'] = self._do_get_url_args()
        if self.__caption__ is not None:
            args['caption'] = self.__caption__
        args['columns'] = self.__fields__
        args['headers'] = self.__headers__
        args['id'] = self.__grid_id__
        args['scroll'] = self.__scroll__
        args['height'] = self.__height__
        if self.__hide_primary_field__:
            args['suppress_id'] = \
                    self.__provider__.get_primary_field(self.__entity__)
        return args

class jqGridTableFiller(TableFiller):
    __possible_field_names__ = ['display_name']
    __hide_primary_field__ = False

    def _calculate_pages(self, total_rows, **kw):
        try:
            limit = int(kw['rows'])
        except:
            limit = None
        current_page = kw.pop('page', 1)
        if limit  is None or limit < 1:
            total_pages = 1
        else:
            total_pages = total_rows / limit + 1
        return current_page, total_pages

    def _get_rows(self, items):
        """ Convert the items into rows that jqGrid understands """
        identifier = self.__provider__.get_primary_field(self.__entity__)
        if self.__hide_primary_field__ == True:
            suppress_id = identifier
        else:
            suppress_id = ''

        rows=[]
        for item in items:
            try:
#                rows.append( { 'id': item[identifier],
#                              'cell':[item[f] for f in
#                                      self.__fields__ if f != suppress_id] , })
                rows.append({f:item[f] for f  in self.__fields__
                             if f != suppress_id})
            except IndexError:
                pass
        return rows

    def _do_search_conditions(self, query, _search, **kw):
        """ Add additional filter objects if we are being called with
        search options """
        if _search != True:
            return query
        try:
            search_field = kw['searchField']
            search_string = kw['searchString']
            search_oper = kw['searchOper']
        except KeyError:
            return query

        op,do_not = self._get_search_op(search_oper)
        if op is None:
            return query.filter('0=1')
        if self.is_relation(search_field):
            # I'll fix this one day when i understand inspect()
            try:
                field = getattr(self.__entity__, search_field+'_id')
            except AttributeError:
                return query.filter('0=1')
        else:
            try:
                field = getattr(self.__entity__, search_field)
            except AttributeError:
                return query.filter('0=1')
        
        if do_not:
            return query.filter(not_(op(field, search_string)))
        return query.filter(op(field, search_string))

    def _do_get_provider_count_and_objs(self, _search=False,  **kw):
        limit = kw.pop('rows', None)
        page = kw.pop('page', 1)
        sidx = kw.pop('sidx', '')
        sord = kw.pop('sord', 'asc')
        kw.pop('nd', False)
        sort_desc =  (sord == 'desc')
        if limit is None or page < 1:
            offset = 0
        else:
            try:
                offset = int(page-1) * int(limit)
            except TypeError:
                offset = 0
        # Extra filters
        conditions = []
        host_id = kw.pop('h', None)
        if host_id is not None and  hasattr(self.__entity__, 'host_id'):
            try:
                conditions.append(self.__entity__.host_id == host_id)
            except (ValueError, TypeError):
                pass
        attribute_id = kw.pop('a', None)
        if attribute_id is not None and  hasattr(self.__entity__, 'attribute_id'):
            try:
                conditions.append(self.__entity__.attribute_id == attribute_id)
            except (ValueError, TypeError):
                pass
#        filters = {'host_id': 1}
#        count, objs = self.__provider__.query(
#            self.__entity__, limit, offset, self.__limit_fields__,
#            sidx, desc, filters=filters,
#            view_fields=self.__possible_field_names__)
        count,objs = self.query( limit, offset, sidx, sort_desc,
                                conditions, _search, **kw)
        self.__count__ = count
        return count, objs

    def _do_sorting(self, query, sort_idx, sort_desc):
        """ Set the sorting on the query based upon the sort
        index (the fieldname) and the sort order """
        if hasattr(self.__entity__, sort_idx):
            try:
                sort_table =\
                        self.__entity__.__mapper__.relationships[sort_idx]
                sort_field = sort_table.table.c['display_name']
                query = query.join(sort_table.table)
            except KeyError:
                try:
                    sort_field =\
                            self.__entity__.__mapper__.c[sort_idx]
                except KeyError:
                    return query
            if sort_desc:
                return query.order_by(desc(sort_field))
            else:
                return query.order_by(sort_field)
        return query

    def get_value(self, value=None, **kw):
        items = super(jqGridTableFiller, self).get_value(value, **kw)
        total_records = self.__count__
        current_page, total_pages = self._calculate_pages(total_records, **kw)
        rows = self._get_rows(items)
        return dict(total=total_pages, page=current_page,
                records=total_records, rows=rows)

    def query(self, limit, offset, sort_idx, sort_desc, conditions, _search,
             **kw):
        """
        Query the database, this is based upon the sprox sa_provider
        query method but is better as its filtering does a lot more
        """
        query = self.__provider__.session.query(self.__entity__).filter(
            and_(*conditions))
        query = self._do_search_conditions(query, _search, **kw)
        count = query.count()

        # sorting
        if sort_idx != '':
            query = self._do_sorting(query, sort_idx, sort_desc)

        if offset is not None:
            query = query.offset(offset)
        if limit is not None:
            query = query.limit(limit)

        objs = query.all()
        return count, objs

    def is_relation(self, field_name):
        """ Return True if field_name is a relation for __entity__ """
        return isinstance(
            self.__entity__.__mapper__.get_property(field_name),
            RelationshipProperty)

    def _get_search_op(self, search_oper):
        """ Translate the search_oper string into a real operator """
        try:
            return COL_OPERATORS[search_oper]
        except KeyError:
            pass
        try:
            return getattr(operator, search_oper),False
        except:
            pass
        return None,False

class DiscoveryFiller(FillerBase):

    def get_value(self, value=None, **kw):
        from rnms.model.host import Host
        from rnms.lib.att_discover import SingleDiscover

        host_id = kw.pop('h', None)
        if host_id is None:
            return {}
        host = Host.by_id(host_id)
        if host is None:
            return {}
        sd = SingleDiscover('attdisc')
        sd.discover(host)
        rows = []
        for atype_id, atts in sd.combined_atts.items():
            atype_name = AttributeType.name_by_id(atype_id)
            for idx, att in atts.items():
                if hasattr(att, 'id'):
                    action = '<a href="{}">Edit</a>'.format(
                        url('/admin/attributes/'+str(att.id)))
                    row_id = ''
                else:
                    action = 'Add'
                    row_id =  '{}-{}'.format(atype_id,idx)
                rows.append({'id': row_id,
                             'cell': (
                                 row_id,
                                 action,
                                 atype_name, 
                                 idx,
                                 att.display_name,
                                 att.oper_state_name(),
                                 'desc',
                                     )})
        return {'records': len(rows), 'rows': rows}
