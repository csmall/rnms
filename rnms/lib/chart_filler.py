
import time

from rnms.model import GraphType, Attribute


class ChartFiller(object):
    """
    Object to fill the JSON data
    """
    attribute_id = None
    graph_type_id = None
    end_time = int(time.time())
    start_time = end_time - 3600

    def __init__(self, a, gt):
        self.attribute_id = a
        self.attribute = Attribute.by_id(a)
        self.graph_type_id = gt

    def display(self):
        """
        Return the dictionary of data to make the graph
        """
        graph_type = GraphType.by_id(self.graph_type_id)
        datasets = []
        mins = {}
        maxs = {}
        lasts = {}
        for line_idx, gt_line in enumerate(graph_type.lines):
            key = 'data{}'.format(line_idx+1)
            ts_data = gt_line.attribute_type_tsdata
            ts_values = ts_data.fetch(self.attribute_id,
                                      self.start_time,
                                      self.end_time)
            datasets.append([key] + ts_values[1])
            mins[key] = gt_line.format_value(min(ts_values[1]), self.attribute)
            maxs[key] = gt_line.format_value(max(ts_values[1]), self.attribute)
            lasts[key] = gt_line.format_value(ts_values[1][-1], self.attribute)
        else:
            datasets.append(['x'] + ts_values[0])
        return {'columns': datasets,
                'mins': mins, 'maxs': maxs, 'lasts': lasts}
