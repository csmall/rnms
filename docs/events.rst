Events
======
Events within Rnms are something that has happened.  They are created by
either a poller backend or a consolidator and have to be linked to a Host 
or an Attribute. Plain Events only have an created time, they do not have
a concept of duration like alarmed Events.

Alarmed Events
==============
If an Event is of an EventType that permits alarms and is associated with
an Attribute then the Event will be marked as an Alarmed Event.  These
items have a stop\_time which can either be set at creation or when 
another Event of the same EventType and Attribute but different state
(usually Up) comes along.

Event Type
==========
All Events have an EventType.  This is specific domain or aspect of an
Attribute or Host. For example an interface Attribute may have an operational
status change or Error count exceeded EventType. Using Event Types means 
it is easier to determine when the Event has been cleared, or its a duplicate
Event.

Event State
===========
All Events have a State. While an EventType will tell you the type of event, 
such an interface status change, or a TCP port result, the state will tell
you more about the Event, such as the interface status is now Down or the
TCP port is now Open.

A departure from JFFNMS is that the Event State has a StateColor which
sets the color in the event viewer and the Attribute and Host maps. Previously
an Events colour was determined by its Severity which was based upon the
EventType. Now the state sets the colour.

How Attribute state is determined
=================================
An Attributes state is inherited purely from the collection of active
alarmed Events for that Attribute.  When Rnms detects that the collection
of Events has changed for an Attribute, all of the active (that is, not
have a corresponding stop event or timed out) alarmed Events for that
Attribute are collected and the one with the lowest priority setting
has its state copied to the Attribute.

As the EventState has a link to the StateColor table, this is what also 
determines the colour of an Attribute in the maps.

The state of a host is similiarly determined using the same method with the
exception that the active alarmed events for all Attributes within are
host are evaluated.


