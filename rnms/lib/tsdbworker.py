# -*- coding: utf-8 -*-
#
# This file is part of the RoseNMS
#
# Copyright (C) 2012-2016 Craig Small <csmall@enc.com.au>
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
import logging
import zmq
import threading
from influxdb import InfluxDBClient
from influxdb.exceptions import InfluxDBClientError

from tg import config

from . import zmqmessage
from . import zmqcore
from .pid import gettid

worker_threads = []

__all__ = ['TSDBClient', 'get_influxclient']


def get_influxclient():
    try:
        influx_dsn = config['influx_dsn']
    except KeyError:
        raise ValueError('Configuration is missing key: influx_dsn')

    return InfluxDBClient.from_DSN(influx_dsn)


class TSDBClient(object):
    """
    Client program to communicate to the Time Series Data Base (TSDB)
    worker.
    """
    available_workers = 0
    waiting_jobs = 0

    def __init__(self, context, zmq_core, required_workers=1):
        self.socket = context.socket(zmq.ROUTER)
        self.socket.bind(zmqmessage.TSDBWORKER_SOCKET)
        zmq_core.register_zmq(self.socket, self.recv)
        self.logger = logging.getLogger('rnms.tsdbc')

        self.jobs_list = []
        self.workers_list = []

        current_workers = len(worker_threads)
        if required_workers > current_workers:
            for dummy in range(required_workers - current_workers):
                worker = TSDBTask(context)
                worker.start()
                worker_threads.append(worker)

    def update(self, attribute_id, fields):
        """
        Update the attribute_id with the dictionary of fields
        """
        if fields == {}:
            return
        self.jobs_list.append({'measurement': 'A{}'.format(attribute_id),
                               'fields': fields})
        self.waiting_jobs += 1
        self.try_send()

    def recv(self, sock):
        """ Called back by the ZMQ poller when we have something to get """
        assert sock == self.socket
        frames = sock.recv_multipart()
        if len(frames) < 3:
            self.logger.error(
                    'zmq socket expected 3 frames, got %d', len(frames))
            return

        worker_addr = frames[0]
        assert frames[1] == ''

        if frames[2] == zmqmessage.READY:
            self.available_workers += 1
            self.workers_list.append(worker_addr)

        self.try_send()

    def try_send(self):
        if self.available_workers == 0 or self.waiting_jobs == 0:
            return

        sent_count = 0
        while sent_count < self.waiting_jobs and \
                sent_count < self.available_workers:
            self.waiting_jobs -= 1
            new_job = self.jobs_list.pop()

            self.available_workers -= 1
            worker_id = self.workers_list.pop()
            self.send_update(worker_id, new_job)

    def send_update(self, worker_addr, message):
        self.socket.send(worker_addr, zmq.SNDMORE)
        self.socket.send('', zmq.SNDMORE)
        self.socket.send(zmqmessage.TSDB_UPDATE, zmq.SNDMORE)
        self.socket.send_json(message)

    def has_jobs(self):
        """ Return True if the TSDBTasks are either doing work,
        or have work to do
        """
        return ((self.waiting_jobs > 0) or
                (len(worker_threads) != self.available_workers))


class TSDBTask(threading.Thread):
    """
    A thread for updating TSDB files
    """
    context = None

    def __init__(self, context):
        threading.Thread.__init__(self)
        self.daemon = True
        self.context = context
        self.logger = logging.getLogger('rnms.tsdbtask')
        self.influx_client = get_influxclient()

    def run(self):
        """ The main loop of the TSDB update thread """
        socket = self.context.socket(zmq.REQ)
        zmqcore.set_id(socket)
        socket.connect(zmqmessage.TSDBWORKER_SOCKET)
        self.logger.info('TSDB worker started PID:{0} Database:{1._database}'.
                         format(gettid(), self.influx_client))

        while True:
            socket.send(zmqmessage.READY)
            frame = socket.recv()
            if frame == zmqmessage.TSDB_UPDATE:
                self._write_points(socket.recv_json())
            else:
                self.logger.error('Got unknown message %s', frame)

    def _write_points(self, args):
        try:
            self.influx_client.write_points([args, ])
        except InfluxDBClientError as err:
            self.logger.error('InfluxDB Error: {}'.format(err.message))
