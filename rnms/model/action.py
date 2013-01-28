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

""" Action template """
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey, Column
from sqlalchemy.types import Integer, Unicode, String
#from sqlalchemy.orm import relation, backref

from rnms.model import DeclarativeBase


class Action(DeclarativeBase):
    __tablename__ = 'actions'
    
    #{ Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    display_name = Column(Unicode(40))
    tag = Column(String(40),nullable=False)
    fields = relationship('ActionField')
    internal_fields = Column(String(120))
    action_type = Column(Integer, nullable=False, default=0) #email,smsclient

    #}
    defined_actions = ('email', 'smsclient')

    def get_trigger_fields(self, trigger):
        """
        Return a dictionary of the action fields based upon internal_fields
        of this model and the action fields of the trigger.
        These will still be the templates, the values from event/alarm
        will be filled in later.
        """
        fields = {}
        for pairs in self.internal_fields.split(','):
            pair = pairs.split(':')
            if len(pair) != 2:
                continue
            fields[pair[0]]=pair[1]
        for trigger_field in trigger.action_fields:
            fields[trigger_field.action_field.tag] = trigger_field.value
        return fields

    def run(self, trigger, user, alarm=None):
        """
        Run this action for an alarm trigger
        """
        subject = fill_fields(trigger.subject, alarm=alarm)

        if self.is_email():
            body = fill_fields(trigger.body, alarm=alarm)
            self.email(user, subject, body)
        elif self.is_smsclient():
            logger.error('A%d T%d: SMSCLIENT not implemented',alarm.attribute.id, trigger.id)
            

        

    def email(self, user, subject, body):
        """
        The email action. Sends an email to the specified user.
        """
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = config['email_from']
        msg['To'] = '{} <{}>'.format(user.user_name, user.email_address)

        s = smtplib.SMTP(config['smtp_server'])
        s.sendmail(config['email_from'], user.email_address, msg.as_string())
        s.quit()

    def is_email(self):
        return self.action_type == 0
    def is_smsclient(self):
        return self.action_type == 1

class ActionField(DeclarativeBase):
    """
    Fields that are used in actions but are presented in the trigger.
    """
    __tablename__ = 'action_fields'
    #{ Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    action_id = Column(Integer, ForeignKey('actions.id'), nullable=False)
    tag = Column(Unicode(40), nullable=False, default=u'')
    display_name = Column(Unicode(40), nullable=False, default=u'')

