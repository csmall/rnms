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
