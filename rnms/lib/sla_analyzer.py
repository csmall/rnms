# -*- coding: utf-8 -*-
#
# This file is part of the RoseNMS
#
# Copyright (C) 2012-2015 Craig Small <csmall@enc.com.au>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <http://www.gnu.org/licenses/>
#

import datetime
import operator
import time
import transaction
from string import Template
from rnms.lib.parsers import NumericStringParser

from rnms.lib.engine import RnmsEngine
from rnms.lib.parsers import fields_regexp
from rnms.model import DBSession, Attribute, Event, Sla, AttributeTypeTSData

SLA_INTERVAL_MINUTES = 30
SLA_RESOLUTION = 300
SLA_WINDOW_SECONDS = 10
SLA_INTERVAL_SECONDS = 180


class SlaException(Exception):
    pass


class CacheSlaRow(object):
    __copy_attrs__ = ('expression', 'oper', 'limit')

    allowed_opers = {
        '=': operator.eq,
        '<>': operator.ne,
        '>': operator.gt,
        '<': operator.lt,
        '>=': operator.ge,
        '<=': operator.le,
        }

    def __init__(self, db_row):
        for copy_attr in self.__copy_attrs__:
            setattr(self, copy_attr, getattr(db_row, copy_attr))

    def agregate_value(self, values):
        """ Return the right agregate for the operator
        """
        if len(values) == 0:
            return None
        if self.oper in ['>', '>=']:
            value = max(values)
        elif self.oper in ['<', '<=']:
            value = min(values)
        else:
            value = sum(values) / len(values)
        try:
            return int(float(value))
        except ValueError:
            raise SlaException("Cannot convert number {}".format(value))

    def operate(self, value):
        """
        Given the calculated output, run the operator against our limit.
        This function does things like > limit etc
        """
        try:
            this_oper = self.allowed_opers[self.oper]
        except KeyError:
            raise SlaException('Invalid operator "{}"'.format(self.oper))
        return this_oper(value, self.limit)

    def eval(self, expression, ts_data):
        """
        Evaluate this specific SLA condition against the given attribute
        """
        nsp = NumericStringParser()
        text_template = Template(expression)
        parsed_vals = []
        for t, values in ts_data:
            if None in values.values():
                continue
            try:
                parsed_vals.append(nsp.eval(
                    text_template.safe_substitute(values)))
            except ZeroDivisionError:
                raise SlaException("Division by Zero \"{}\"".format(
                    expression))
            except:
                raise SlaException("NSP Error in \"{}\"".format(
                    expression))

        agregate_value = self.agregate_value(parsed_vals)
        return (self.operate(agregate_value),
                "{} ({}) {} {}".format(expression, agregate_value,
                                       self.oper, self.limit))


class CacheSLA(object):
    """ Cached version of the SLA model. This version has the
    actual calculation logic in it too.
    """
    __copy_attrs__ = (
        'attribute_type_id', 'event_text', 'threshold')

    def __init__(self, db_sla):
        for copy_attr in self.__copy_attrs__:
            setattr(self, copy_attr, getattr(db_sla, copy_attr))
        self.rows = [CacheSlaRow(row) for row in db_sla.rows]

    def analyze(self, logger, attribute):
        cond_results = []
        event_details = []
        start_time = int(time.time()-SLA_INTERVAL_MINUTES * 60)

        ts_data = None

        for row_idx, row in enumerate(self.rows):
            expression = attribute.parse_string(row.expression)
            ts_data = self.update_ts_data(ts_data, expression, attribute,
                                          start_time)
            if ts_data is None:
                return None, event_details
            # AND/OR remove the last two items from stack
            # and replace with reasult
            if (row.expression == 'AND'):
                if len(cond_results) < 2:
                    logger.error('AND sla condition needs 2 results')
                    continue
                result = cond_results[-1] and cond_results[-2]
                logger.info(
                    'A%d Row%d: %s AND %s := %s',
                    attribute.id, row_idx, cond_results[-1],
                    cond_results[-2], result)
                cond_results = cond_results[:-2] + [result]
            elif (row.expression == 'OR'):
                if len(cond_results) < 2:
                    logger.error('OR sla condition needs 2 results')
                    continue
                result = cond_results[-1] or cond_results[-2]
                logger.info(
                    'A%d Row%d: %s OR %s := %s',
                    attribute.id, row_idx, cond_results[-1],
                    cond_results[-2], result)
                cond_results = cond_results[:-2] + [result]
            else:
                try:
                    (result, details) = row.eval(expression, ts_data)
                except SlaException as err:
                    logger.error("A%d Row%d: Error %s",
                                 attribute.id, row_idx, err)
                    return None, event_details
                logger.info(
                    'A%d Row%d: %s',
                    attribute.id, row_idx, row.expression)
                logger.info(
                    'A%d Row%d: %s := %s',
                    attribute.id, row_idx, details, result)
                cond_results.append(result)
                if result is False:
                    event_details.append(details)
        if (len(cond_results) < 1 or cond_results[-1] is False):
            return False, event_details
        return True, event_details

    def update_ts_data(self, ts_data, expression, attribute,
                       start_time):
        """ Update the ts_data list of (time, value dict) tuples
        fields are $tsdb_name in expression """
        for new_field in set(fields_regexp.findall(expression)):
            if ts_data is None or new_field not in ts_data:
                tsdb = AttributeTypeTSData.by_name(
                    attribute.attribute_type_id, new_field)
                if tsdb is None:
                    raise SlaException(
                        '\'{}\' is not an Attribute field nor TS Data'.format(
                            new_field))
                new_data = tsdb.fetch(attribute.id, start_time)
                if new_data is None:
                    continue
                if ts_data is None:
                    # First time, so this series adds the time
                    ts_data = [(t, {}) for t in new_data[0]]
                new_dict = dict(zip(*new_data))
                for t, values in ts_data:
                    try:
                        values[new_field] = new_dict[t]
                    except KeyError:
                        # If we cannot find value for any field the entire
                        # set goes for that time
                        del ts_data[(t, values)]
        return ts_data

    def update_rrd_values(self, rrd_values, attribute, text,
                          start_time, end_time):
        """
        Given a string and existing rrd_values dictionary, add in the
        missing values
        """
        new_fields = set(fields_regexp.findall(text))
        for new_field in new_fields:
            if new_field not in rrd_values:
                rrd_values[new_field] = \
                    attribute.get_rrd_value(new_field, start_time, end_time)
        return rrd_values


class SLAanalyzer(RnmsEngine):
    """
    Analyze all of the SLA paramters on the attributes
    """
    attribute_ids = None
    host_ids = None
    forced_attributes = False
    next_find_attribute = datetime.datetime.min

    def __init__(self, attribute_ids=None, host_ids=None,
                 zmq_context=None, do_once=True):
        super(SLAanalyzer, self).__init__('rnms.sla', zmq_context)

        self.attribute_ids = attribute_ids
        self.host_ids = host_ids
        self.do_once = do_once
        self.load_config()

    def load_config(self):
        self.slas = {}
        for sla in DBSession.query(Sla):
            self.slas[sla.id] = CacheSLA(sla)
        self.logger.debug(
            "SLA Analyzer loaded %d rules.\n", len(self.slas))

    def analyze(self):

        if self.do_once:
            next_sla_time = None
        else:
            next_sla_time = datetime.datetime.now()

        while True:
            attributes = self.find_new_attributes(next_sla_time)
            self.update_next_find_attribute()
            for attribute in attributes:
                if not self.zmq_core.poll(0.0):
                    return
                if self.end_thread:
                    return

                if attribute.is_down():
                    self.logger.debug('A%d: is DOWN, skipping', attribute.id)
                    continue
                self.logger.debug(
                    'A%d: START on %s',
                    attribute.id, attribute.sla.display_name)
                self.analyze_attribute(attribute)
                attribute.update_sla_time()

            if self.do_once or self.end_thread:
                break
            transaction.commit()

            # otherwise we wait
            if self._sleep_until_next() is False:
                return
            next_sla_time = datetime.datetime.now() +\
                datetime.timedelta(seconds=SLA_WINDOW_SECONDS)

    def find_new_attributes(self, next_sla_time):
        """ Add new attributes that need to have their SLA analyzed """
        return Attribute.have_sla(
            next_sla_time, self.attribute_ids, self.host_ids)

    def _sleep_until_next(self):
        """
        Stay in this loop until we need to go into the main loop again.
        Returns False if we have broken out of the poll
        """
        next_attribute = Attribute.next_sla_analysis()
        if next_attribute is None:
            return self.sleep(self.next_find_attribute)
        else:
            self.logger.info(
                "Next SLA Analysis #%d at %s",
                next_attribute.id, next_attribute.next_sla.ctime())
            if self.next_find_attribute > next_attribute.next_sla:
                self.next_find_attribute = next_attribute.next_sla
            return self.sleep(self.next_find_attribute)

    def update_next_find_attribute(self):
        self.next_find_attribute = datetime.datetime.now() +\
            datetime.timedelta(seconds=SLA_INTERVAL_SECONDS)

    def analyze_attribute(self, attribute):
        """
        Analyze the SLA against the given attribute
        """
        try:
            sla = self.slas[attribute.sla_id]
        except KeyError:
            self.logger.error("A:%d - SLA id %d not found",
                              attribute.id, attribute.sla_id)
            return
        sla_result, event_details = sla.analyze(self.logger, attribute)
        if sla_result is False:
            self.logger.debug('A%d: Final Result: False', attribute.id)
        elif sla_result is True:
            self.logger.debug('A%d: Final Result: True', attribute.id)
            new_event = Event.create_sla(
                attribute, sla.event_text, ', '.join(event_details))
            if new_event is None:
                self.logger.error('A%d: Cannot create event', attribute.id)
            else:
                DBSession.add(new_event)
