# -*- coding: utf-8 -*-
#
# This file is part of the RoseNMS
#
# Copyright (C) 2013-2015 Craig Small <csmall@enc.com.au>
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
"""
Module for the master daemon that runs all the sub-processes for
RoseNMS
Daemonizing code comes from
http://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/
"""
import os
import threading
import sys

import zmq

from tg import config

from rnms.lib.pid import check_proc_alive, gettid
from rnms.lib.poller import Poller
from rnms.lib.consolidate import Consolidator
from rnms.lib.sla_analyzer import SLAanalyzer
from rnms.lib.discovery.attributes import AttDiscover
from rnms.lib.snmptrapd import SNMPtrapd
from rnms.lib import zmqmessage, zmqcore


class RnmsDaemon(object):
    """
    Master object for the RoseNMS daemon. This daemon is responsible
    for starting other sub-threads either continuously or at particular times.
    """
    enable_poller = True
    enable_consolidator = True
    args = None
    threads = None
    __set_pidfile__ = False

    def __init__(self, log):
        self.log = log
        self.threads = {}
        self.end_threads = False
        self.timeout = 10

    def run(self, parsed_args):
        """ The entry point for the RNMS daemon """
        if not parsed_args.foreground:
            self.daemonize()
        self.zmq_core = zmqcore.ZmqCore()
        self.zmq_context = zmq.Context()
        self.control_socket = zmqmessage.control_server(self.zmq_context)
        self.create_pidfile()

        self._create_info_socket()

        self.poller = Poller(zmq_context=self.zmq_context, do_once=False)
        self.threads['poller'] = threading.Thread(
            target=self.poller.main_loop,
            name='poller')
        self.threads['poller'].start()

        self.consolidator = Consolidator(zmq_context=self.zmq_context,
                                         do_once=False)
        self.threads['consolidator'] = threading.Thread(
            target=self.consolidator.consolidate, name='consolidator')
        self.threads['consolidator'].start()

        self.sla_analyzer = SLAanalyzer(zmq_context=self.zmq_context,
                                        do_once=False)
        self.threads['sla_analyzer'] = threading.Thread(
            target=self.sla_analyzer.analyze, name='sla_analyzer')
        self.threads['sla_analyzer'].start()

        self.att_discover = AttDiscover(zmq_context=self.zmq_context,
                                        do_once=False)
        # self.threads['att_discover'] = threading.Thread(
        # target=self.att_discover.discover, name='att_discover')
        # self.threads['att_discover'].start()

        self.snmptrapd = SNMPtrapd(zmq_context=self.zmq_context)
        self.threads['snmptrapd'] = threading.Thread(
            target=self.snmptrapd.run,
            name='snmptrapd')
        self.threads['snmptrapd'].start()
        # main loop
        while True:
            try:
                if not self._poll():
                    return -1
                ret_val = self._check_threads()
                if ret_val is not None:
                    return ret_val
            except KeyboardInterrupt:
                self.log.debug('User Interrupt Pressed, shutting down')
                self._shutdown()

    def _shutdown(self):
        """ Method that is called to shutdown the daemon """
        self.control_socket.send(zmqmessage.IPC_END)
        self.end_threads = True
        self.timeout = 1

    def _poll(self):
        """ Poll the ZMQ socket and handle any requests """
        return self.zmq_core.poll(10)

    def _check_threads(self):
        """ Check the status of all sub-threads. Return None if
        all is good, otherwise the return value """
        waiting_threads = []
        for tname, tobj in self.threads.items():
            if tobj.is_alive():
                if self.end_threads:
                    waiting_threads.append(tname)
            elif not self.end_threads:
                self.log.critical('Thread %s has died.', tname)
                self._shutdown()
                return -1
        if self.end_threads:
            if waiting_threads == []:
                self.log.debug('All threads finished, exiting')
                self.del_pidfile()
                return 0
            else:
                self.log.debug('Waiting for threads {}'.
                               format(', '.join(waiting_threads)))
        return None

    def info_callback(self, socket):
        frames = socket.recv_multipart()
        if frames[0] == zmqmessage.IPC_INFO_REQ:
            self.info_socket.send(zmqmessage.IPC_INFO_REP, zmq.SNDMORE)
            self.info_socket.send_json(
                    {'thread_count': threading.active_count(),
                     'daemon_tid': gettid(),
                     'tasks': [
                         {'name': tname,
                          'alive': tobj.isAlive(),
                          }
                         for tname, tobj in self.threads.items()]})
        else:
            self.error('Info socket received invalid command')

    def _create_info_socket(self):
        self.info_socket = zmqmessage.info_server(self.zmq_context)
        self.zmq_core.register_zmq(self.info_socket, self.info_callback)

    def daemonize(self):
        """ Daemonize the process """
        try:
            pid = os.fork()
            if pid > 0:
                # exit first parent
                sys.exit(0)
        except OSError, e:
            sys.syserr.write("fork #1 failed: {} ({})\n".
                             format(e.errno, e.strerror))

        #  Decouple from parent environment
        os.chdir("/")
        os.setsid()
        os.umask(0)

        # Do second fork
        try:
            pid = os.fork()
            if pid > 0:
                # Exit from the second parent
                sys.exit(0)
        except OSError, e:
            sys.stderr.write("fork #2 failed: {} ({})\n".format(
                e.errno, e.strerror))

        # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        si = file("/dev/null", "r")
        so = file("/dev/null", "a+")
        se = file("/dev/null", "a+")
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

    def create_pidfile(self):
        """ Create and check for PID file """
        pidfile = config['rnmsd_pid_file']
        piddir = os.path.dirname(pidfile)
        if not os.path.isdir(piddir):
            self.log.error(
                'Exiting, pidfile directory %s doesn\'t exist',
                piddir)
            sys.exit(1)
            return
        try:
            pf = file(pidfile)
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if pid:
            if check_proc_alive(pid):
                self.log.error(
                        'Exiting, pidfile %s already exists for'
                        'running process %d',
                        pidfile, pid)
                sys.exit(1)
                return
            self.log.info(
                    'Stale pidfile %s exists, deleting.',
                    pidfile)
            self.del_pidfile()

        try:
            pf = open(pidfile, 'w+')
            pf.write("{}\n".format(os.getpid()))
        except IOError as err:
            self.log.error(
                "Unable to write self.pidfile %s: %s\n",
                pidfile, err)
            sys.exit(1)
            return

    def del_pidfile(self):
        """ Delete our self.pidfile """
        pidfile = config['rnmsd_pid_file']
        os.remove(pidfile)


def main():
    rnmsd = RnmsDaemon(__name__)
    return rnmsd.run()

if __name__ == '__main__':
    sys.exit(main())
