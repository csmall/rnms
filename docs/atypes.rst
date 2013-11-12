Attribute Types
===============
The types of Attributes that can be discovered and polled is setup in the
configuration. RNMS comes out with a variety of Attribute Types and you
can add your own.

Apache
------
Polls the server status for an Apache webserver. Rnms displays the statistics
that this feature exposes, such as number of workers or accesses.

APC
---
Polls the APC UPS devices that have SNMP enabled.

Alteon Load Balancers
---------------------
Alteon Load Balancers are reasonably old devices but still in use in some
places.  As well as the System Information, which tracks the usual things
like CPU loads and memory usage, the Real and Virtual Servers and Services
are tracked for their utilisation and response times.  The state of these
elements is also tracked and can send alarms.

Applications
------------


BGP Neighbors
-------------
These Attribute Types are the BGP (Border Gateway Protocol) peers.  The
number of advertised and received routes, as well as messages in and out
are tracked.  The state of the Attribute follows the state of the peer.
Information comes via SNMP using the BGP peer MIB based on RFC1269.

Brocade FC Ports
----------------

Brocade Sensors
---------------

Cisco 802.11X Device
--------------------

Cisco NAT
---------

Cisco PIX
---------

Cisco Power Supply
------------------

Cisco SA Agent
--------------

Cisco System Info
-----------------
An Attribute Type for the CPU or system of Cisco devices.  Displays the
memory and CPU statistics of the device as well as the TCP connection
count.

Devices that have SNMP enabled and a Cisco enterprise for sysObjectId are
polled for this system information.

Cisco Temperature
Cisco Voltage

Compaq CPQ MIB
--------------
Monitors the Compaq CPQ environmental elements such as Fans, Power Supplies,
Temperature and Physical Drives.

Dell Chassis
------------

Fibre Channel Ports
-------------------

IIS Webserver Information
-------------------------

Linux/Unix System Info
----------------------

NTP
---
The poller checks the status of NTP servers on the host by using NTP standard
control messages.  If the host has at least one synchronised peer it is 
considered synchronised and up.


OS/400 System Info
------------------

Physical Interfaces
-------------------
This is the standard ifTable interfaces that are discovered via SNMP.
Almost any device that supports SNMP will have some interfaces from ifTable.
The ip address table is also polled at the same time and if there is a match
the addresses are applied to the interface.

The usual statistics such as octect and packet counts as well as errors are
polled and the attribute follows the ifOper column of the ifTable for status.


Reachable
---------
All devices that have an IP address are assumed to be reachable. The Reachable
Attribute Type requires fping and/or fping6 to be installed.  Round trip
time (RTT) and packetloss are graphed for these Attribute Types.

Sensors
-------

Solaris System Info
-------------------

Storage
-------
Storage Attribute Types are discovered via SNMP by scanning the hrStorageTable.
This table considers storage to be mainly disk drives as well as memory as
"storage". The graphs for these types show the total and used amount for
the device. There is no state tracked.

TCP Ports
---------
Systems can be port scanned to find open TCP ports. These ports then have
their response time captured by connecting to the ports and, if SNMP is 
available, the number of connections on that port.  There is also an option
to check the content from the port for specific text.

For TCP ports to be autodiscovered, the nmap or nmap6 binary needs to be 
installed.

UPS and Lines
-------------
Queries for either a standard RFC1628 or a Mitsubishi UPS using SNMP. Both
the device status (such as load or on-battery) and the input and output
lines can be tracked.

Windows System Info
