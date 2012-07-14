# -*- coding: utf-8 -*-
#
# This file is part of the Rosenberg NMS
#
# Copyright (C) 2012 Craig Small <csmall@enc.com.au>
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

__all__ = [ 'init', 'info', 'warn' ]

logger = None

def init(name, loglevel=None):
    global logger
    logging.basicConfig(format='%(asctime)-6s: %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(name)
    if loglevel is not None:
        numeric_level = getattr(logging, loglevel.upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError('Invalid log level: %s' % loglevel)
    logger.setLevel(numeric_level)

def info(*args):
    logger.info(*args)

def warn(*args):
    logger.warn(*args)

def error(*args):
    logger.warn(*args)
