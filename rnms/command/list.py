
from cliff.lister import Lister


class List(Lister):

    def take_action(self, parsed_args):
        return(('Foo', 'Bar'), (('a', 'b'),('a', 'c')))
