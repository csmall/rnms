#
# Structures for Admin screens
from rnms import model

class base_table(object):
    __headers__ = {
        'id': 'ID',
        'display_name': 'Name', 'host': 'Host',
        'attribute_type': 'Attribute Type',
        'admin_state': 'Admin State', 
        'user': 'Owner',
    }
    def created(self, obj):
        return obj.created.strftime('%Y-%b-%d %H:%M:%S')


class attribute(base_table):
    __entity__ = model.Attribute
    __limit_fields__ = ('id', 'host', 'display_name', 'attribute_type',
                        'user','created')

class host(base_table):
    __entity__ = model.Host
    __limit_fields__ = ('id', 'display_name', 'zone', 'created')

class zone(base_table):
    __entity__ = model.Zone
    __limit_fields__ = ('id', 'display_name', 'short_name')
