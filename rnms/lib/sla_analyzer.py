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
from rnms.model import DBSession, Attribute, Event, Sla

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

    def operate(self, output):
        """
        Given the calculated output, run the operator against our limit.
        This function does things like > limit etc
        """
        try:
            output = int(float(output))
        except ValueError:
            raise SlaException("Cannot convert number {}".format(output))
            return False
        try:
            this_oper = self.allowed_opers[self.oper]
        except KeyError:
            raise SlaException('Invalid operator "{}"'.format(self.oper))
        return this_oper(output, self.limit)

    def eval(self, rrd_values):
        """
        Evaluate this specific SLA condition against the given attribute
        """
        nsp = NumericStringParser()
        text_template = Template(self.expression)
        parsed_expression = text_template.safe_substitute(rrd_values)
        try:
            expression_output = nsp.eval(parsed_expression)
        except ZeroDivisionError:
            raise SlaException("Division by Zero \"{}\"".format(
                parsed_expression))
        except:
            raise SlaException("NSP Error in \"{}\"".format(
                parsed_expression))
        return (self.operate(expression_output),
                "{} ({}) {} {}".format(parsed_expression, expression_output,
                                       self.oper, self.limit))


class CacheSLA(object):
    __copy_attrs__ = (
        'attribute_type_id', 'event_text', 'threshold')

    def __init__(self, db_sla):
        for copy_attr in self.__copy_attrs__:
            setattr(self, copy_attr, getattr(db_sla, copy_attr))
        self.rows = [CacheSlaRow(row) for row in db_sla.rows]

    def analyze(self, logger, attribute):
        cond_results = []
        event_details = []
        end_time = str(int(time.time()/SLA_INTERVAL_SECONDS) *
                       SLA_INTERVAL_SECONDS)
        start_time = 'e-{}m'.format(SLA_INTERVAL_SECONDS * 60)
        rrd_values = attribute.get_fields()

        for row_count, cond in self.rows:
            try:
                rrd_values = self.update_rrd_values(
                    rrd_values, attribute, cond.expression,
                    start_time, end_time)
            except KeyError as errmsg:
                logger.error('A%d %s', attribute.id, errmsg)
                return None, event_details
            if len(rrd_values) == 0:
                return None, event_details
            # AND/OR remove the last two items from stack
            # and replace with reasult
            if (cond.expression == 'AND'):
                if len(cond_results) < 2:
                    logger.error('AND sla condition needs 2 results')
                    continue
                result = cond_results[-1] and cond_results[-2]
                logger.info(
                    'A%d Row%d: %s AND %s := %s',
                    attribute.id, row_count, cond_results[-1],
                    cond_results[-2], result)
                cond_results = cond_results[:-2] + [result]
            elif (cond.expression == 'OR'):
                if len(cond_results) < 2:
                    logger.error('OR sla condition needs 2 results')
                    continue
                result = cond_results[-1] or cond_results[-2]
                logger.info(
                    'A%d Row%d: %s OR %s := %s',
                    attribute.id, row_count, cond_results[-1],
                    cond_results[-2], result)
                cond_results = cond_results[:-2] + [result]
            else:
                try:
                    (result, details) = cond.eval(rrd_values)
                except SlaException as err:
                    logger.error("A%d Row%d: Error %s",
                                 attribute.id, row_count, err)
                    return None, event_details
                logger.info(
                    'A%d Row%d: %s',
                    attribute.id, row_count, cond.expression)
                logger.info(
                    'A%d Row%d: %s := %s',
                    attribute.id, row_count, details, result)
                cond_results.append(result)
                if result is False:
                    event_details.append(details)
        logger.info(
            "A%d VALUES %s",
            attribute.id,
            ', '.join(
                ['{0}({1})'.format(k, v) for (k, v) in rrd_values.items()]))
        if (len(cond_results) < 1 or cond_results[-1] is False):
            return False, event_details
        return True, event_details

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
