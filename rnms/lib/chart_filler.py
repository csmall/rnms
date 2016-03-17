
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
        for line_idx, gt_line in enumerate(graph_type.lines):
            ts_data = gt_line.attribute_type_tsdata
            ts_values = ts_data.fetch(self.attribute_id,
                                      self.start_time,
                                      self.end_time)
            datasets.append({
                'label': ts_data.display_name,
                'data': ts_values[1],
                })
        data = {
                'labels': ts_values[0],
                'datasets': datasets,
                }
        return data
