
import os
import sys
from argparse import ArgumentParser
import sqlalchemy 
from paste.deploy import appconfig
from rnms.config.environment import load_environment
from rnms import model
import transaction

conf = appconfig('config:' + os.path.abspath('development.ini'))
load_environment(conf.global_conf, conf.local_conf)

es=model.DBSession.query(model.Event).filter(model.Event.event_type_id>1)
for e in es:
    print(e.text())
