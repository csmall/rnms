
"""
RRD Workers - update the RRD files with these workers
The workers are dumb, they just do what they're told to do.
"""
import threading
import logging
import zmq

from rnms.lib import zmqmessage
from rnms.lib import zmqcore

worker_threads = []

class RRDClient(object):
    """
    """
    socket = None
    frontend = None
    workers_list = None
    available_workers = 0

    jobs_list = None
    waiting_jobs = 0

    def __init__(self, context, zmq_core, required_workers=1):
        self.socket = context.socket(zmq.ROUTER)
        self.socket.bind(zmqmessage.RRD_ROUTER)
        zmq_core.register_zmq(self.socket, self.recv)
        self.logger = logging.getLogger('rrdc')

        self.jobs_list = []
        self.workers_list = []

        current_workers = len(worker_threads)
        if required_workers > current_workers:
            for dummy in range(required_workers - current_workers):
                worker = RRDTask(context)
                worker.start()
                worker_threads.append(worker)


    def update(self, filename, value):
        self.jobs_list.append((filename, value))
        self.waiting_jobs += 1
        self.try_send()

    def recv(self, sock):
        """ Called back by the ZMQ poller when we have something to get """
        assert sock == self.socket
        frames = sock.recv_multipart()
        if len(frames) < 3:
            self.logger.error('zmq socket expected 3 frames, got %d',len(frames))
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
        while sent_count < self.waiting_jobs and sent_count < self.available_workers:
            self.waiting_jobs -= 1
            new_job = self.jobs_list.pop()

            self.available_workers -= 1
            worker_id = self.workers_list.pop()
            self.send_update(worker_id, *new_job)

    def send_update(self,worker_addr, filename, value):
        self.socket.send(worker_addr, zmq.SNDMORE)
        self.socket.send('', zmq.SNDMORE)
        self.socket.send(zmqmessage.RRD_UPDATE, zmq.SNDMORE)
        self.socket.send('{}:{}'.format(filename, value))

    def has_jobs(self):
        """ Return True if the RRD workers are either doing work, 
        or have work to do
        """
        return ((self.waiting_jobs > 0) or (len(worker_threads) != self.available_workers))

class RRDTask(threading.Thread):
    """
    A thread for updating RRD files
    """
    rrd_dir = None
    context = None

    def __init__(self, context):
        threading.Thread.__init__(self)
        self.daemon = True
        self.context = context
        self.logger = logging.getLogger('rrdw')

    def run(self):
        """ The main loop of the RRD update thread """
        import os

        rrdworker = self.context.socket(zmq.REQ)
        zmqcore.set_id(rrdworker)
        rrdworker.connect(zmqmessage.RRD_WORKER)
        self.logger.info('RRD worker started PID:%d', os.getpid())

        while True:
            rrdworker.send(zmqmessage.READY)
            frames = rrdworker.recv_multipart()
            if frames[0] == zmqmessage.RRD_UPDATE and len(frames) == 2:
                self._rrd_update(frames[1])
            else:
                self.logger.error('Got unknown message %s',frames[0])

    def _rrd_update(self, recv_frame):
        import rrdtool
        try:
            filename,value = recv_frame.split(':')
            float(value)
        except ValueError:
            self.logger.error('bad rrd_update value %s',recv_frame)
            return
        try:
            #self.logger.debug('update %s to %s',filename, value)
            rrdtool.update(filename, "N:{0}".format(value))
        except rrdtool.error as errmsg:
            self.logger.error('RRD error - %s', errmsg)


