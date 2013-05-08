
from sprox.tablebase import TableBase
from sprox.fillerbase import TableFiller

from tw2.jqplugins.jqgrid import jqGridWidget


class jqGridGrid(jqGridWidget):
    id = 'jq-grid-id'
    params = ['columns', 'column_widths',]
    options = {
            'pager': 'hosts-grid-pager',
            'datatype': 'json',
            'viewrecords': True,
            'imgpath': 'scripts/jqGrid/themes/green/images',
            'width': 900,
            'height': 'auto',
            }
    columns = None

    def __init__(self, action, attrs, value):
        super(jqGridGrid, self).__init__()
        self.options['url'] = action
        self.options['colNames'] = self._get_colnames()
        self.options['colModel'] = self._get_colmodel()

    def _get_colnames(self):
        colnames = []
        for col in self.columns:
            try:
                colnames.append(self.headers[col])
            except KeyError:
                colnames.append(col.capitalize())
        return colnames

    def _get_colmodel(self):
        colmodel  = []
        default_width =  self.default_column_width
        for colname in self.columns:
            try:
                width = self.column_widths[colname]
            except KeyError:
                width = default_width
            colmodel.append({
                'name': colname,
                'width': width,
            })
        return colmodel


class jqGridTableBase(TableBase):
    """ A table widget """
    __base_widget_type__ = jqGridGrid
    __url__ = None
    __column_options__ = {}
    __retrieves_own_value__ = True

    def _do_get_widget_args(self):
        args = super(jqGridTableBase, self)._do_get_widget_args()
        if self.__url__ is not None:
            args['url'] = self.__url__
        args['columns'] = self.__fields__
        args['column_options'] = self.__column_options__
        args['headers'] = self.__headers__
        return args

class jqGridTableFiller(TableFiller):
    def _calculate_pages(self, total_rows, **kw):
        try:
            limit = int(kw['rows'])
        except:
            limit = None
        current_page = kw.pop('page', 1)
        if limit  is None or limit < 1:
            total_pages = 1
        else:
            total_pages = total_rows / limit
        return current_page, total_pages

    def _get_rows(self, items):
        """ Convert the items into rows that jqGrid understands """
        identifier = self.__provider__.get_primary_field(self.__entity__)
        rows=[]
        for item in items:
            try:
                rows.append( { 'id': item[identifier],
                    'cell':[ item[f] for f in self.__fields__] , })
            except IndexError:
                pass
        return rows

    def _do_get_provider_count_and_objs(self, _search=False,  **kw):
        limit = kw.pop('rows', None)
        page = kw.pop('page', 1)
        kw.pop('sidx', None)
        kw.pop('sord', 'asc')
        kw.pop('nd', False)
        #FIXME sort orders
        desc =  False
        order_by = None
        if limit is None:
            offset = 0
        else:
            try:
                offset = int(page) * int(limit)
            except TypeError:
                offset = 0
        count, objs = self.__provider__.query(
            self.__entity__, limit, offset, self.__limit_fields__,
            order_by, desc, filters={})
        self.__count__ = count
        return count, objs

    def get_value(self, value=None, **kw):
        items = super(jqGridTableFiller, self).get_value(value, **kw)
        total_records = self.__count__
        current_page, total_pages = self._calculate_pages(total_records, **kw)
        rows = self._get_rows(items)
        return dict(total=total_pages, page=current_page,
                records=total_records, rows=rows)


