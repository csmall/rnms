#
# Structures for Admin screens
from rnms import model
from tg import url

def click(model_name, mod_id, name):
    return '<a href="{}">{}</a>'.format(
            url('/{}/{}'.format(model_name, mod_id)),
            name)

class base_table(object):
    __headers__ = {
        'id': 'ID',
        'display_name': 'Name', 'host': 'Host',
        'attribute_type': 'Attribute Type',
        'admin_state': 'Admin State', 
        'event_type': 'Event Type',
        'user': 'Owner',
    }
    __column_widths__ = {
        'id': 5,
        'created': 30,
    }
    def created(self, obj):
        return obj.created.strftime('%Y-%b-%d %H:%M:%S')


class attribute(base_table):
    __entity__ = model.Attribute
    __limit_fields__ = ('id', 'host', 'display_name', 'attribute_type',
                        'user','created')
    __omit_fields__ = ('__actions__',)
    def display_name(self,obj):
        return click('attributes',obj.id, obj.display_name)
    def host(self, obj):
        return click('hosts', obj.host_id, obj.host.display_name)

class attribute_mini(base_table):
    __entity__ = model.Attribute
    __hide_primary_field__ = True
    __omit_fields__ = ('__actions__',)
    __limit_fields__ = ('id', 'attribute_type', 'display_name', 'user')

    def attribute_type(self, obj):
        return click('attributes',obj.id, obj.attribute_type.display_name)
    def display_name(self,obj):
        return click('attributes',obj.id, obj.display_name)

class host(base_table):
    __entity__ = model.Host
    __limit_fields__ = ('id', 'display_name', 'zone', 'created')
    __omit_fields__ = ('__actions__',)
    __column_widths__ = {'id': 10, 'display_name': 30, 'zone': 30, 'created':30}

    def zone(self, obj):
        return click('zones', obj.zone_id, obj.zone.display_name)
    def display_name(self, obj):
        return '<a href="{}">{}</a>'.format(
            url('/hosts/{}'.format(obj.id)),
            obj.display_name)

class host_list(host):
    """ Used for viewing not editing a host list """
    __hide_primary_field__ = True
    __omit_fields__ = ('__actions__',)

class zone(base_table):
    __entity__ = model.Zone
    __limit_fields__ = ('id', 'display_name', 'short_name')

class event(base_table):
    __entity__ = model.Event
    __hide_primary_field__ = True
    __omit_fields__ = ('__actions__',)
    __limit_fields__ = ('id', 'created', 'host', 'attribute',
                        'event_type', 'description' )
    __column_widths__ = {'created': 25, 'event_type': 10, 'description': '100%'}

    def host(self, obj):
        return '<div class="severity{}"><a href="{}">{}</a></div>'.format(
            obj.event_state.severity_id,
            url('/hosts/{}'.format(obj.host_id)),
            obj.host.display_name)
    def attribute(self, obj):
        return '<div class="severity{}"><a href="{}">{}</a></div>'.format(
            obj.event_state.severity_id,
            url('/attributes/{}'.format(obj.attribute_id)),
            obj.attribute.display_name)


    def description(self, obj):
        return obj.text()
