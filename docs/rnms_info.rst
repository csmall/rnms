=========
rnms_info
=========

SYNOPSYS
========
  **rnms_info** [**-dhqv**] [**-c** *config*] [**-p** *pidfile*] *qtype* *id*...

DESCRIPTION
===========
**rnms_info** is a tool to query the database on various models that RoseNMS
contains.  These queries are meant to assist administrators in troubleshooting,
for example working out what Host a particular Attribute belongs to.

The info tool can query the following models: attributes, attribute types,
hosts, poller sets, autodiscovery policies, slas and triggers.  The second
parameter is the ID of the item you want to query.


OPTIONS
=======

-c file, --config file    Read configuration settings from *file*
-d, --debug            Turn on debugging
-h, --help             Show help message and exit
-p file, --pidfile file  Write process PID to *file*
-q, --quiet            Log critical messages only
-v, --verbose          Increase verbosity of logging

ID                    ID of the items you want information about

QTYPE                 Type of query (model) to perform, see `DESCRIPTION`_ for list

EXAMPLE
=======
For example, to look at attribute #2, you would use the following 
commands::
  
  $ rnms_info attribute 2
  
  ============================================================
  Attribute           | 2: Async5 (index: 5)
  ------------------------------------------------------------
  Host                 | 5: Cisco1700
  State (admin/oper)   | down/down
  Attribute Type       | 4: Physical Interfaces
  Poller Set           | 42: SNMP Interface (enabled:True)
  Poll Priority        | False
  SLA                  | 1: No SLA
  Created              | 2012-03-11 10:34:58
  Next SLA             | 2013-09-30 12:26:29.878441
  Next Poll            | 2013-10-07 14:58:20.189101
  ------------------------------------------------------------
  Fields
  IP Address           | 192.168.101.1
  IP Mask              | 255.255.255.252
  Peer Address         | 192.168.101.2
  Speed                | 38000

Each type of query will display detailed information about the requested
object.  There can also be cross references, so to see information about
the above attributes host, you would query host 5.


SEE ALSO
========
* `RoseNMS Documentation <http://rosenberg-nms.readthedocs.org/en/latest/>`_
* **rnms_poller** (1)
* **rnmsd** (1)
