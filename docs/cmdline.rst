Command Line
============
Rnms has many command line utilities that can either be used to run the
system in various modes or used for debugging or informational purposes.

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
 
