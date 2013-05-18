# -*- coding: utf-8 -*-
#
# This file is part of the Rosenberg NMS
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
import sys
import logging

import sqlalchemy
import transaction

from rnms.lib.cmdline import RnmsCommand
from rnms.lib.jffnms_config import JffnmsConfig
from rnms.lib import jffnms_import as jimport

class JffnmsImporter(RnmsCommand):
    dbhandle = None
    translate = {}

    def real_command(self):
        self.logger = logging.getLogger('rnms')
        self.jconf = JffnmsConfig()
        self.jconf.parse(self.options.jffnms_conf)
        self.open_jffnms_db()
        # FIXME check for delete
        jimport.do_delete(self)

        for importer in ('zone', 'user', 'host', 'interface', 'attribute',
                         'event' ):
            imp_func = getattr(jimport, 'import_'+importer)
            ret = imp_func(self)
            if ret is None:
                return 1
            self.translate[importer] = ret
        if self.options.dry_run == False:
            transaction.commit()


        self.print_conf_shell()
        self.close_jffnms_db()

    def standard_options(self):
        super(JffnmsImporter, self).standard_options()
        self.parser.add_argument(
            '-n', '--dry-run',
            action='store_true',
            dest='dry_run',
            help='Do not insert records into database',
        )
        self.parser.add_argument(
            '--jffnms-conf',
            action='store',
            dest='jffnms_conf',
            help='Directory where JFFNMS configuration file is',
            default='/home/wwwroot/jffnms/conf',
            metavar='DIR'
        )
    
    def open_jffnms_db(self):
        """ Create the JFFNMS Database handler """
        jffnms_db_engine = sqlalchemy.create_engine(sqlalchemy.engine.url.URL(
            self.jconf.get('db_type'),
            username = self.jconf.get('dbuser'),
            password = self.jconf.get('dbpass'),
            host = self.jconf.get('dbhost'),
            database = self.jconf.get('db'),
        ))
        self.logger.debug('Connecting to JFFNMS database.')
        self.dbhandle = jffnms_db_engine.connect()

    def close_jffnms_db(self):
        """ close JFFNMS Database connector """
        self.dbhandle.close()
        self.dbhandle = None


    def host_id(self,jffnms_id):
        return self.translate['host'].get(jffnms_id,1)
    def user_id(self,jffnms_id):
        return self.translate['user'].get(jffnms_id,1)
    def zone_id(self,jffnms_id):
        return self.translate['zone'].get(jffnms_id,1)

    def print_conf_shell(self):
        print "JFFNMS_PATH="+self.jconf.get('rrd_real_path')
        print "IDS='"+' '.join(
            [str(x)+':'+str(y) for x,y in self.translate['attribute'].items()])+"'"

def main():
    imp = JffnmsImporter('info')
    return imp.run()

if __name__ == '__main__':
    sys.exit(main())
