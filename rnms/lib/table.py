
from sprox.tablebase import TableBase
from sprox.fillerbase import TableFiller, FillerBase
from tg import url

from tw2.jqplugins.jqgrid import jqGridWidget

from rnms.model import AttributeType

class jqGridGrid(jqGridWidget):
    """
    Standard jQuery UI grid for the TableBase
    """
    id = None
    url = None
    params = ['id', 'scroll', 'height', 'caption', 'columns', 'column_widths', 'default_column_width']
    options = {
            'datatype': 'json',
            #'autowidth': True,
            'imgpath': 'scripts/jqGrid/themes/green/images',
            }
    columns = None
    suppress_id = None
    caption = None
    scroll = False
    height = None

    def __init__(self, action=None):
        super(jqGridGrid, self).__init__()
        if action is not None:
            self.options['url'] = action
        else:
            self.options['url'] = self.url
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
            colmodel.append({
                'name': colname,
                'index': colname,
                'width': width,
            })
        return colmodel


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

    def _do_get_url(self):
        try:
            if self.attribute_id is not None:
                return '{}?a={}'.format(self.__url__, self.attribute_id)
        except AttributeError:
            pass
        try:
            if self.host_id is not None:
                return '{}?h={}'.format(self.__url__, self.host_id)
        except AttributeError:
            pass
        return self.__url__

    def _do_get_widget_args(self):
        args = super(jqGridTableBase, self)._do_get_widget_args()
        if self.__url__ is not None:
            args['url'] = self._do_get_url()
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
                rows.append( { 'id': item[identifier],
                              'cell':[item[f] for f in
                                      self.__fields__ if f != suppress_id] , })
            except IndexError:
                pass
        return rows

    def _do_get_provider_count_and_objs(self, _search=False,  **kw):
        limit = kw.pop('rows', None)
        page = kw.pop('page', 1)
        sidx = kw.pop('sidx', None)
        sord = kw.pop('sord', 'asc')
        kw.pop('nd', False)
        desc =  (sord == 'desc')
        if sidx == '':
            sidx = None
        if limit is None or page < 1:
            offset = 0
        else:
            try:
                offset = int(page-1) * int(limit)
            except TypeError:
                offset = 0
        # Extra filters
        filters = {}
        host_id = kw.pop('h', None)
        if host_id is not None and  hasattr(self.__entity__, 'host_id'):
            try:
                filters['host_id'] = int(host_id)
            except (ValueError, TypeError):
                pass
        attribute_id = kw.pop('a', None)
        if attribute_id is not None and  hasattr(self.__entity__, 'attribute_id'):
            try:
                filters['attribute_id'] = int(attribute_id)
            except (ValueError, TypeError):
                pass
        count, objs = self.__provider__.query(
            self.__entity__, limit, offset, self.__limit_fields__,
            sidx, desc, filters=filters,
            view_fields=self.__possible_field_names__)
        self.__count__ = count
        return count, objs

    def get_value(self, value=None, **kw):
        items = super(jqGridTableFiller, self).get_value(value, **kw)
        total_records = self.__count__
        current_page, total_pages = self._calculate_pages(total_records, **kw)
        rows = self._get_rows(items)
        return dict(total=total_pages, page=current_page,
                records=total_records, rows=rows)


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
