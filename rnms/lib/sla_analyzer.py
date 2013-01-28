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

# Import models for rnms
import logging
from rnms import model

logger = logging.getLogger('rnms')

class SLAanalyzer():
    """
    Analyze all of the SLA paramters on the attributes
    """
    attribute_ids=None
    host_ids=None

    def __init__(self, attribute_ids=None, host_ids=None):
        self.attribute_ids=attribute_ids
        self.host_ids = host_ids

    def analyze(self):
        attributes = model.Attribute.have_sla(self.attribute_ids,self.host_ids)
        for attribute in attributes:
            if attribute.is_down():
                logger.info('A%d: is DOWN, skipping',attribute.id)
                continue
            logger.info('A%d: START on %s',attribute.id, attribute.sla.display_name)
            attribute.sla.analyze(attribute)
