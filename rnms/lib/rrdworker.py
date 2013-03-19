
"""
RRD Workers - update the RRD files with these workers
"""
import zmq
import threading
import logging

from tg import config

from rnms.lib import zmqmessage
from rnms.lib import zmqcore

WORKER_PATH = 'inproc://rrd-update'

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

    def __init__(self, context, required_workers=1):
        self.logger = logging.getLogger('rrdc')
        self.socket = context.socket(zmq.ROUTER)
        self.socket.bind(WORKER_PATH)
        zmqcore.register(self.socket, self.recv)
        self.jobs_list = []
        self.workers_list = []

        current_workers = len(worker_threads)
        if required_workers > current_workers:
            for dummy in range(required_workers - current_workers):
                worker = RRDTask(context)
                worker.start()
                worker_threads.append(worker)


    def update(self, rrd, value):
        self.jobs_list.append((rrd,value))
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

        if frames[2] == zmqmessage.INIT:
            self.send_config(worker_addr)
            return

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
        self.socket.send('{}:{}'.format(filename,value))

    def send_config(self,worker_addr):
        """ 
        Send the configuration back to the worker
        """
        self.socket.send(worker_addr, zmq.SNDMORE)
        self.socket.send('', zmq.SNDMORE)
        self.socket.send(zmqmessage.CONF, zmq.SNDMORE)
        self.socket.send(config['rrd_dir'])
    

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
        import rrdtool

        rrdworker = self.context.socket(zmq.REQ)
        zmqcore.set_id(rrdworker)
        rrdworker.connect(WORKER_PATH)
        self.logger.info('RRD worker started PID:%d', os.getpid())

        conf = zmqmessage.init_and_config(rrdworker)
        if conf is None:
            self.logger.critical('rrdworker got bad config')
            return
        self.rrd_dir = conf
        if not os.path.isdir(self.rrd_dir):
            self.logging.error('rrd_dir config setting %s is not a directory.', self.rrd_dir)
            return

        while True:
            rrdworker.send(zmqmessage.READY)
            frames = rrdworker.recv_multipart()
            if frames[0] == zmqmessage.RRD_UPDATE and len(frames) == 2:
                if self.rrd_dir is None:
                    self.logger.error('Got update before config')
                    return
                else:
                    try:
                        filename,value = frames[1].split(':')
                        float(value)
                    except ValueError:
                        self.logger.error('bad rrd_update value %s',frames[1])
                    else:
                        pathname = ''.join(self.rrd_dir, os.sep, filename)
                        myrrd = rrd.RRD(filename=pathname)
                        myrrd.bufferValue(int(time.time()),value)
                        try:
                            myrrd.update()
                        except 


                    print 'update {}/{}={}'.format(self.rrd_dir, filename, value)
            else:
                self.logger.error('Got unknown message %s',frames[0])
