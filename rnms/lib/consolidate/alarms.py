# -*- coding: utf-8 -*-
#
# This file is part of the RoseNMS
#
# Copyright (C) 2012,2013 Craig Small <csmall@enc.com.au>
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
import datetime

from tg import config
from sqlalchemy import and_

from rnms.lib.parsers import fill_fields
from rnms.model import DBSession, Alarm, Trigger

def check_alarm_stop_time(logger):
    """
    Run through all the alarms that have check_stop_time set to
    see if we have reached the time to close off the alarm.
    This generally clears a SLA alarm on an Attribure after it has
    expired, for example.

    Returns a set of Attribute IDs that have had a status change
    """
    now = datetime.datetime.now()
    changed_attributes = set()
    alarms = DBSession.query(Alarm).filter(and_(Alarm.check_stop_time == True, Alarm.stop_time < now))
    for alarm in alarms:
        alarm.check_stop_time = False
        changed_attributes.add(alarm.attribute_id)
    return changed_attributes


def check_alarm_triggers(logger):
    alarms = DBSession.query(Alarm).filter(Alarm.processed == False)
    triggers = Trigger.alarm_triggers()
    logger.info('%d Alarms to process', alarms.count())
    if alarms.count() == 0:
        return
    for alarm in alarms:
        for trigger in triggers:
            rule_result = False
            for rule in trigger.rules:
                rule_result = rule.eval(rule_result, alarm)
                if rule_result == True and rule.stop == True:
                    break

            if rule_result == True:
                if trigger.email_owner == True:
                    logger.debug('A%d T%d: email to %s',alarm.attribute.id, trigger.id, alarm.attribute.user.user_name)
                    email_action(trigger, alarm.attribute.user, alarm=alarm)
            if trigger.email_users == True:
                sent_users = []
                for trigger_user in trigger.users:
                    sent_users.append(alarm.attribute.user.user_name)
                    trigger.email_action(trigger, trigger_user,alarm=alarm)
                if sent_users != [] :
                    logger.debug('A%d T%d: email to %s',alarm.attribute.id, trigger.id, ','.join(sent_users))
        alarm.processed = True
    transaction.commit()



def email_action(trigger, user, alarm):
    """
    Send an email for this alarm to the specified user
    """
    import smtplib
    from email.mime.text import MIMEText

    subject = fill_fields(trigger.subject, alarm=alarm)
    body = fill_fields(trigger.body, alarm=alarm)

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = config['email_from']
    msg['To'] = '{} <{}>'.format(user.user_name, user.email_address)

    s = smtplib.SMTP(config['smtp_server'])
    s.sendmail(config['email_from'], user.email_address, msg.as_string())
    s.quit()

