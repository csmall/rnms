
SNMP Traps
==========
SNMP traps are messages that are sent from SNMP Agents, such as routers or
servers to a SNMP Manager, such as Rosenberg NMS.

For the purposes of how they are handled, a trap has the following fields:
* Source IP address
* Trap OID
* One or more VarBinds which are OID value keypairs, similair to a python dictionary.

SNMP v1 traps use a different format but they are converted to use the same
format.

SNMP Trap Daemon
----------------
When the main rnmsd is started up, a thread is opened to create a receiver
for SNMP traps. Traps are sent via UDP and may be high frequency or even
spoofed (where the source IP address is forged). The daemon does two
checks on the incoming trap.

First, the trap source IP address is checked against the known list of
configured hosts. To minimize impact on the database, the result is cached
in a local dictionary.  If there is no Host with that IP address, the trap
is discarded.

Secondly the trap is checked against duplicates. Essentially if the trap
from the same source IP address with the same trap OID is seen within 5
seconds of another trap with the same properties, it is discarded. A lot
of implementations send several traps for the same event and this ensures there is only one forwarded.  The disadvantage is that if there is a down trap and
then very soon after an up trap and they use the same OID the second
one won't be processed.

How Rosenberg NMS treats traps
------------------------------
Rosenberg NMS assumes that a particular trap (identified by a trap OID)
is for a specific Attribute Type. For example the ifDown traps describe
something happening to a physical interface, while a temperature alarm
trap is connected to either a sensor or perhaps the element (e.g. CPU).
If there are multiple Attribute Types that could be applied to the same
trap OID, multiple Trap Matches can be given for that OID and then the
Trap Match commands (e.g. matching on description) can be used to determine
which is the correct one for this trap.

At set intervals, currently 30 seconds, a trap consolidator is run on the
raw traps. The input data is Host ID, trap OID and the VarBinds. The 
consolidator first looks for all Trap Matches that first match exactly the
trap OID and then optionally secondly on the VarBinds. The point of the
Trap Match is to find an Attribute and a value or multiplie values 
that are passed along to the backend.

Just like Pollers have several commands, Trap Matches do too that process
the VarBinds of the trap to find the Attribute. Only Attributes that have
the correct type (defined by the Trap Match) will be looked at.

Trap Match Commands
-------------------
The following commands are used by Trap Match within the consolidator to
locate the attribute.

match\_index\_state : The Attribute is found by examining the VarBind
with the specified OID and matching against the VarBind value and the
Attribute's index field.

The value is either fixed or if it is an OID the VarBinds are searched
for this OID. The result can be mapped to another value before returning,
such as 1=down,2=up.
  
