Console Scripts
===============
While most of the time both administrators and users will use the web GUI
to interact with Rosenberg, the back-end console scripts are essential
for the running of the program.

Logging
-------
The utilities have a standard set of command line options for logging
levels. These levels are converted into standard python logging levels.
With no options, the default logging level is Warning. From loudest to
quietest, the options are:

-d or --debug
  Set logging level to Debug
-v or --verbose
  Set logging level to Info
Nothing
  The default is here at Warning
-q or --quiet
  Set logging level to Critical
 
rnmsd
-----
All of the required engines can be run in a single program called rnmsd.
This program has a small master thread which launches and monitors all the 
sub-threads such as pollers and trap daemons. For most installations, 
starting this program is all that is required.

rnms_info
---------
While administrators can directly interrogate the database, the 
rnms\_info tool can do simple queries against the database.  The
command line is:

  rnms\_info _query\_type_ _ids_

The info tool can query the following models: attributes, attribute types,
hosts, poller sets, autodiscovery policies, slas and triggers.  The second
parameter is the ID of the item you want to query.

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

