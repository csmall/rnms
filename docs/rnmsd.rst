=====
rnmsd
=====

SYNOPSYS
========
  **rnmsd** [**-hqv**] [**-c** *config*] [**-p** *pidfile*]

DESCRIPTION
===========
**rnmsd** is the main RoseNMS daemon.  This main program spawns off
several threads to take care of the back-end of the NMS systems. For
most installations, starting this program is all that is required.
The threads are

* Poller - collects statistics and status on attributes
* Consolidator - converts raw events such as syslog lines into real
  events and alarms
* SNMP Trapd - collects SNMP traps from remote devices and stores
  them for subsequent Consolidator processing

OPTIONS
=======

-c file, --config file      Read configuration settings from *file*
-d, --debug            Turn on debugging
-h, --help             Show help message and exit
-p file, --pidfile file  Write programs PID to *pidfile*
-q, --quiet            Log critical messages only
-v, --verbose          Increase verbosity of logging

SEE ALSO
========
* `RoseNMS Documentation <http://rosenberg-nms.readthedocs.org/en/latest/>`_
* **rnms_poller** (1)
* **rnms_info** (1)
