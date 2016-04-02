
import tw2.core as twc

from rnms.lib.resources import bootstrap_table_js, bootstrap_table_css


class BootstrapTable(twc.Widget):
    """
    Widget that provides a Table that works well with the bootstrap
    templates
    """
    template = 'rnms.templates.widgets.bootstrap_table'
    resources = [
                 bootstrap_table_js,
                 bootstrap_table_css]

    columns = twc.Param('List of (column, title) tuples')
    hidden_columns = twc.Param('List of hidden column names', default=[])
    data_url = twc.Param('URL for the JSON query')
    detail_url = twc.Param('URL to go to detail pane on a row of the table',
                           default=None)
    enable_search = twc.Param('set to true to enable table search',
                              default=False)
    filter_params = twc.Param('Dictionary of extra filtering', default={})
    row_formatter = twc.Param('Dictionary of (column,JSfunc) for formatting',
                              default={})
    row_style = twc.Param('JS function for format style', default={})
    fit_panel = twc.Param('If its a small table to fit whole panel',
                          default=False)
    striped = twc.Param('sety to false to now have striped rows', default=True)
    sort_name = twc.Param('Default sort column', default='id')
    sort_asc = twc.Param('Boolean sort ascending, set false for desc',
                         default=True)
    have_checkbox = twc.Param('Boolean: Rows have a selection checkbox',
                              default=False)
    have_radio = twc.Param('Boolean: Rows have a selection radio',
                           default=False)
