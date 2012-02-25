
from tw2.jqplugins import jqgrid
from rnms.model import Attribute

class AttributeGrid(jqgrid.jqGridWidget):
    id ='attribute-grid-id'
    options = {
            'pager' : 'attribute-grid-pager',
            'url' : '/attributes/jqsumdata',
            'datatype': 'json',
            'colNames' : ['Name', 'Oper State', 'Admin State'],
            'colModel' : [
                {
                    'name' : 'display_name',
                } , {
                    'name' : 'oper_state',
                    'width': 100,
                },{
                    'name' : 'admin_state',
                    'width': 100,
                },],
            'rowNum': 15,
            'rowList': [15,30,50],
            'viewrecords': True,
            'imgpath': 'scripts/jqGrid/themes/green/images',
            'height': 'auto',
            }   

    pager_options = { "search" : True, "refresh" : True, "add" : False,
            "edit": False }
     


