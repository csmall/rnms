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
import ctypes
import os
import errno

SYS_gettid = 186

try:
    libc = ctypes.CDLL('libc.so.6')
except:
    libc = None


def gettid():
    """
    Return the thread ID if possible, otherwise return the PID
    """
    if libc is not None:
        try:
            return libc.syscall(SYS_gettid)
        except:
            pass
    return os.getpid()


def check_proc_alive(pid):
    """
    Return True if the process with the given PID is alive
    """
    try:
        os.kill(pid, 0)
    except OSError as err:
        if err.errno == errno.ESRCH:
            return False
    return True
