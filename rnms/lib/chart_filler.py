
import time
import datetime


class ChartFiller(object):
    """
    Object to fill the JSON data
    """
    preset_time = None

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
        self.calculate_times()
        if self.graph_type.template == 'mtuarea':
            self.calc_data_mtuarea()
        elif self.graph_type.template == 'pctarea':
            self.calc_data_pctarea()
        else:
            self.calc_data_lines()

    def calc_data_pctarea(self):
        """ A graph that is a stacked area of percents of each item """
        num_lines = len(self.graph_type.lines)
        self.datasets = [['data{}'.format(idx+1)]
                         for idx in range(0, num_lines)]
        raw_values = [
            line.attribute_type_tsdata.fetch(
                self.attribute.id,
                self.start_time,
                self.end_time)
            for line in self.graph_type.lines]
        for idx in range(0, len(raw_values[0][0])):
                total = sum([raw_values[col][1][idx]
                             for col in range(0, num_lines)])
                for line in range(0, num_lines):
                    self.datasets[line].append(
                        min(
                            max(float(raw_values[line][1][idx])/total, 0.0),
                            100.0))
        self.datasets.append(['x'] + raw_values[0][0])
        for line, gt_line in enumerate(self.graph_type.lines):
            key = 'data{}'.format(line+1)
            self.mins[key] = gt_line.format_value(
                    min(self.datasets[line][1:]), self.attribute)
            self.maxs[key] = gt_line.format_value(
                    max(self.datasets[line][1:]), self.attribute)
            self.lasts[key] = gt_line.format_value(
                    self.datasets[line][1:][-1], self.attribute)

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
                raw_total = None
                raw_used = None
            if raw_total is None or raw_used is None:
                frees.append(None)
                useds.append(None)
                continue

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

    def calculate_times(self):
        # The default 1hr
        self.end_time = int(time.time())
        self.start_time = self.end_time - 3600

        if self.preset_time is not None:
            try:
                time_val = int(self.preset_time[:-1])
            except:
                return
            try:
                time_unit = self.preset_time[-1]
            except:
                return
            if time_unit == 'M':
                interval = datetime.timedelta(minutes=time_val)
            elif time_unit == 'H':
                interval = datetime.timedelta(hours=time_val)
            elif time_unit == 'd':
                interval = datetime.timedelta(days=time_val)
            elif time_unit == 'w':
                interval = datetime.timedelta(weeks=time_val)
            elif time_unit == 'm':
                interval = datetime.timedelta(days=time_val*30)
            else:
                return
            self.start_time = int(self.end_time - interval.total_seconds())
