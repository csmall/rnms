
import time

from rnms.model import GraphType


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
        self.graph_type_id = gt

    def display(self):
        """
        Return the dictionary of data to make the graph
        """
        graph_type = GraphType.by_id(self.graph_type_id)
        datasets = []
        for line_idx, rrd_line in enumerate(graph_type.lines):
            rrd = rrd_line.attribute_type_rrd
            rrd_values = rrd.fetch(self.attribute_id,
                                   self.start_time,
                                   self.end_time)
            datasets.append({
                'label': 'mylabel',
                'data': [v[0] for v in rrd_values[2]]
                })
        data = {
                'labels': range(0, len(rrd_values[2])),
                'datasets': datasets,
                }
        return data
