import tw2.core as twc

__all__ = ['TabPanel', ]


class TabPanel(twc.CompoundWidget):
    """
    A set of tabs which have a series of children to display
    """
    template = 'rnms.templates.widgets.tab_panel'
    tabs = twc.Param('List of (\'tab-id\', \'tab title\') tuples')
