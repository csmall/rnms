
import time


class ChartFiller(object):
    """
    Object to fill the JSON data
    """
    end_time = int(time.time())
    start_time = end_time - 3600

    def __init__(self, attribute, graph_type):
        self.attribute = attribute
        self.graph_type = graph_type
        self.datasets = []
        self.mins = {}
        self.maxs = {}
        self.lasts = {}

    def calc_data(self):
        """
        Return the dictionary of data to make the graph
        """
        if self.graph_type.template == 'mtuarea':
            self.calc_data_mtuarea()
        else:
            self.calc_data_lines()

    def calc_data_mtuarea(self):
        (ts_mult, ts_tot, ts_used) = self.graph_type.lines
        multipliers = ts_mult.attribute_type_tsdata.fetch(
            self.attribute.id,
            self.start_time,
            self.end_time)
        totals = ts_tot.attribute_type_tsdata.fetch(
            self.attribute.id,
            self.start_time,
            self.end_time)
        raw_useds = ts_used.attribute_type_tsdata.fetch(
            self.attribute.id,
            self.start_time,
            self.end_time)

        frees = ['data1', ]
        useds = ['data2', ]
        for idx, multiplier in enumerate(multipliers[1]):
            try:
                raw_total = totals[1][idx]
                raw_used = raw_useds[1][idx]
            except IndexError:
                continue  # skip this one, missing data
            # FIXME multi_op operations on tsdata.multiplier
            total = raw_total * multiplier
            used = raw_used * multiplier
            free = max(total - used, 0.0)
            frees.append(free)
            useds.append(used)
        self.datasets = [frees, useds, ['x'] + multipliers[0]]
        self.maxs = {
            'data1': ts_mult.format_value(max(frees[1:]), self.attribute),
            'data2': ts_used.format_value(max(useds[1:]), self.attribute)}
        self.mins = {
            'data1': ts_mult.format_value(min(frees[1:]), self.attribute),
            'data2': ts_used.format_value(min(useds[1:]), self.attribute)}
        self.lasts = {
            'data1': ts_mult.format_value(frees[-1], self.attribute),
            'data2': ts_used.format_value(useds[-1], self.attribute)}

    def calc_data_lines(self):
        for line_idx, gt_line in enumerate(self.graph_type.lines):
            key = 'data{}'.format(line_idx+1)
            ts_data = gt_line.attribute_type_tsdata
            ts_values = ts_data.fetch(self.attribute.id,
                                      self.start_time,
                                      self.end_time)
            self.datasets.append([key] + ts_values[1])
            self.mins[key] = gt_line.format_value(
                min(ts_values[1]), self.attribute)
            self.maxs[key] = gt_line.format_value(
                max(ts_values[1]), self.attribute)
            self.lasts[key] = gt_line.format_value(
                ts_values[1][-1], self.attribute)
        else:
            self.datasets.append(['x'] + ts_values[0])

    def display(self):
        if self.datasets == []:
            self.calc_data()
        return {'columns': self.datasets,
                'mins': self.mins, 'maxs': self.maxs, 'lasts': self.lasts}
