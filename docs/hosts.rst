Hosts and Attributes
====================

.. _zone:

Zones
-----
Zones are groupings of Hosts. They can be used for displaying a group together
or for making a set of hosts visible.

Hosts
-----
Hosts are the devices that you want to manage.  They are essentially something
that has an IP address (either IPv4 or IPv6) and generally would also have
some sort of SNMP Agent. The Agent is not essential but is very useful as
most :ref:`Attribute Types` will need SNMP. The main exeption being
:ref:`Reachability <at-reachability>`,
:ref:`TCP Ports <at-tcpports>` and :ref:`NTP <at-ntp>`.

As expected, Hosts have a management address, a name, optionally three 
`SNMP Communities`_ (read only, read/write and trap) plus some other
parameters such as `Autodiscovery Policies`_. Hosts also belong to 
a single :ref:`Zone <zone>`.

Hosts do not have an User but may have a default User for Attributes
found during Autodiscovery.  This makes sense when a single Host
may service many User's services. For example, a common switch may
have user A on port 1 and user B on port 2, or a particular
server may have several websites owned by different users.

Attributes
----------
An Attribute is one of the major models that is used in Rosenberg NMS.
It is effectively something that you want to monitor or track within
a Host.  Attributes will have RRD values to update or a status to track
or perhaps both these options.

The simplest idea of an Attribute is a physical interface.  This 
Attribute Type has counters that turn into graphs such as an error
or packet rate and the operational and administrative status that
change the state of the Attribute.  All other Attributes are variations
of this idea, but follow the same basic concept.

Besides the Host it is bound to, an Attribute can have a SLA. The 
particular SLA that can be assigned to an Attribute is based upon the
Attribute Type. The SLA uses the last 30 minutes of data to determine
if the data are within some specification.

.. _poll-priority:

Attributes can have a poll priority. While it is not essential to set
an Attribute for a host with a priority, it greatly helps with the
efficiency of the poller.

Attributes with the poll priority are selected before normal Attributes.
If Attributes within a host with poll priority set are down, then the
remaining Attributes within that host are no polled.  This means that
with careful selection of prioritized Attributes, if an entire host
is down then the poller doesn't waste effort attempting to get to
the host.  The most common Attribute Type to assign for priority
is Reachability. The idea being that if you cannot ping the host,
then you cannot reach it and it doesn't make sense to attempt to
get any more data out of the device.

With a prioritized Attribute down for a Host, only the prioritized
Attributes are polled.
