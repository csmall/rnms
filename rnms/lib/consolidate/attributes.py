# -*- coding: utf-8 -*-
#
# This file is part of the RoseNMS
#
# Copyright (C) 2013 Craig Small <csmall@enc.com.au>
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
import transaction

from rnms.model import DBSession, Attribute

def check_all_attributes_state(logger):
    """ Recalculate all Attributes Oper state
    This is done when the consolidator is first started
    """
    logger.debug('Recalculating all Attributes Oper state')
    attributes = DBSession.query(Attribute)
    if attributes is None:
        return
    for attribute in attributes:
        attribute.calculate_oper()
    transaction.commit()

def check_attribute_state(attribute_ids, logger):
    """ Recalculate the given Attributes Oper state """
    if len(attribute_ids) == 0:
        return
    attributes = DBSession.query(Attribute).filter(Attribute.id.in_(list(attribute_ids)))
    if attributes.count() == 0:
        return
    logger.info('%d Attribute States to process', attributes.count())
    for attribute in attributes:
        attribute.calculate_oper()
    transaction.commit()
