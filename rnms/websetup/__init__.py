# -*- coding: utf-8 -*-
"""Setup the RoseNMS application"""

import logging
from schema import setup_schema
import bootstrap
from tsdb_setup import tsdb_setup


from rnms.config.environment import load_environment

__all__ = ['setup_app']

log = logging.getLogger(__name__)


def setup_app(command, conf, vars):
    """Place any commands to setup rnms here"""
    load_environment(conf.global_conf, conf.local_conf)
    setup_schema(command, conf, vars)
    tsdb_setup()
    bootstrap.bootstrap(command, conf, vars)
