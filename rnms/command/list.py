
from cliff.lister import Lister
from rnms import model


class List(Lister):
    """ List items within the RNMS database """

    def get_parser(self, prog_name):
        query_types = list(x[:-5] for x in dir(self) if x[-5:] == '_info')
        parser = super(List, self).get_parser(prog_name)
        parser.add_argument(
            action='store',
            dest='qtype',
            type=str,
            choices=query_types,
            help='Query Type:' + ', '.join(query_types),
            metavar='<query type>')
        return parser

    def take_action(self, parsed_args):
        try:
            real_info = getattr(self, parsed_args.qtype+'_info')
        except AttributeError:
            raise RuntimeError(
                'Unknown query type "{}".'.format(parsed_args.qtype))
        return real_info(parsed_args)

    def attribute_info(self, parsed_args):
        attributes = model.DBSession.query(model.Attribute).\
            join(model.AttributeType).\
            order_by(model.Attribute.id)
        return(
            ('ID', 'Name', 'Host', 'HID', 'Type', 'TID',),
            ((
                a.id, a.display_name, a.host.display_name, a.host_id,
                a.attribute_type.display_name, a.attribute_type_id,
            ) for a in attributes)
        )
