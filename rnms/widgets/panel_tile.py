import tw2.core as twc


class PanelTile(twc.CompoundWidget):
    """
    Compound Widget that creates a panel tile that holds other widgets
    """
    template = 'rnms.templates.widgets.panel_tile'
    title = twc.Param('Title for this panel tile', default='Title')
    subtitle = twc.Param('Subtitle for this panel tile', default=None)
    fullwidth = twc.Param('Full width? True/False', default=False)
    fillrow = twc.Param('3/4 to fill row True/False', default=False)
    fullheight = twc.Param('Full height? True/False', default=False)
