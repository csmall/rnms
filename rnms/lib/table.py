
from sprox.tablebase import TableBase
from sprox.fillerbase import TableFiller

from tw2.jqplugins.jqgrid import jqGridWidget

class jqGridGrid(jqGridWidget):
    args = None
    params = ['jsId', 'url', 'args','pks','xml_fields','fields',
              'default_column_width']
    pks = None
    url = None
    jsId = None
    id = 'hello'
    default_column_width = '10em'
    fields = {}
    pager_options = { 'search': True, 'refresh': True, 'add': False, }
    options = {
        'pager': 'jqgrid-pager',
        'dataype': 'json',
        'viewrecords': True,
        'imgpath': 'scripts/jgGrid/themes/green/images',
        'height': 'auto',
    }

    def __init__(self, action, attrs, value):
        print  'Widget init fields'#, self.fields
        self.options['url'] = action
        colwidth =  int(self.default_column_width.strip('em')) * 16
        self.options['colModel'] = [{'name':
                                     f[0],'width':colwidth} for f in self.fields]
        super(jqGridGrid, self).__init__()

class jqGridTableBase(TableBase):
    """ A table widget """
    __base_widget_type__ = jqGridGrid
    __url__ = None
    __column_options__ = {}
    __retrieves_own_value__ = True

#    def __init__(self, args):
#        print 'TableBase init'
#        super(jqGridTableBase, self).__init__(args)

#    def display(self, *args, **kw):
#        print 'TableBase display'
#        return super(jqGridTableBase, self).display(*args, **kw)

#    def _do_init_attrs(self):
#        print 'Tablebase do init attrs '
#        attrs = super(jqGridTableBase, self)._do_init_attrs()
#        print 'Tablebase do init attrs ', attrs

#    def _do_get_fields(self):
#        print 'TableBase do get fields'
#        fields = super(jqGridTableBase, self)._do_get_fields()
#        return fields

    def _do_get_widget_args(self):
        print 'TableBase do get widget args start'
        args = super(jqGridTableBase, self)._do_get_widget_args()
        if self.__url__ is not None:
            args['url'] = self.__url__
        #args['columns'] = self.__fields__
        #args['column_options'] = self.__column_options__
        #args['headers'] = self.__headers__
        args['jsId'] = self.__id__
        print 'TableBase do get widget args', args
        return args

class jqGridTableFiller(TableFiller):
#    def __init__(self, arg):
#        print 'table filler init', arg
#        super(jqGridTableFiller, self).__init__(arg)

    def _calculate_pages(self, offset, limit, records):
        if offset is None or limit is None or records == 0:
            return 1,1
        page =  offset / limit  + 1
        total = records / limit
        return page, total

    def _get_rows(self, items):
        """ Convert the items into rows that jqGrid understands """
        identifier = self.__provider__.get_primary_field(self.__entity__)
        rows=[]
        for item in items:
            try:
                rows.append( { 'id': item[identifier], 'cell': item, })
            except IndexError:
                pass
        return rows

    def _do_get_provider_count_and_objs(self, _search=False,  **kw):
        limit = kw.pop('rows', None)
        page = kw.pop('page', 1)
        kw.pop('sidx', None)
        kw.pop('sord', 'asc')
        kw.pop('nd', False)
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
        print 'before super filler get value'
        value = super(jqGridTableFiller, self).get_value(value, **kw)
        print 'after super filler get value'
        offset = kw.pop('start', None)
        limit  = kw.pop('count', None)
        order_by = kw.pop('sort', None)
        print 'filler get value', offset, limit
        desc = False
        if order_by is not None and order_by.startswith('-'):
            order_by = order_by[1:]
            desc = True
        items = super(jqGridTableFiller, self).get_value(
            value, limit=limit, offset=offset,
            order_by=order_by, desc=desc, **kw)
        records = len(items)
        page, total = self._calculate_pages(offset, limit, records)
        return {'records': 1, 'total': 1, 'rows': [{'cell': [u'<a href="/hosts/1">No Host</a>', u'Default Zone', 'ttt'], 'id': 1}], 'page': 1}
        return dict(total=1, page=1, records=1, rows=rows)


