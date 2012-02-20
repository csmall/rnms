from rnms import model

from tw2.jqplugins.jqplot import JQPlotWidget
from tw2.jqplugins.jqplot.base import categoryAxisRenderer_js, barRenderer_js
from tw2.core import JSSymbol
from tw2 import rrd
from tw2.jqplugins.jqgrid import SQLAjqGridWidget

class AttributeGrid(SQLAjqGridWidget):
    id = 'attribute-grid'
    entity = model.Attribute
    excluded_columns = ['id']

    prmFilter = {'stringResult': True, 'searchOnEnter': True}

    options = {
            'url': '/tw2_controllers/db_jqgrid/',
            'rowNum': 15,
            'viewrecords': True,
            'imgpath': 'scripts/jqGrid/themes/green/images',
            'shrinkToFit': True,
            'height': 'auto',
            }

   

class LogPlot(JQPlotWidget):
    id = 'awesome-logplot'
    interval = 2000
    resources = JQPlotWidget.resources + [
        categoryAxisRenderer_js,
        barRenderer_js,
    ]
 
    options = {
        'seriesDefaults' : {
            'renderer': JSSymbol('$.jqplot.BarRenderer'),
            'rendererOptions': { 'barPadding': 4, 'barMargin': 10 }
        },
        'axes' : {
            'xaxis': {
                'renderer': JSSymbol(src="$.jqplot.CategoryAxisRenderer"),
            },
            'yaxis': {'min': 0, },
        }
    }

class RRDWidget(rrd.FlatRRDFlotWidget):
    id='foobar'
    datasource_name = 'data'
