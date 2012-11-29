.. Rosenberg NMS documentation master file, created by
   sphinx-quickstart on Thu Nov 29 22:23:50 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Rosenberg NMS's documentation!
=========================================

Contents:

.. toctree::
   :maxdepth: 2



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Rosenberg NMS (rnms) is, as the name implies, a Network Management System.
What this means is rnms is a piece of software that gathers information
on devices out on a network and tries to meaningfully interpret them to 
make monitoring and managment simpler.

rnms is written in python and is based upon the Turbogears 2 web framework.
The basic concept is largely built around the ideas that were put into
another NMS program called JFFNMS.

History of Rosenberg NMS
========================
Rnms is the third network management system that I have worked on. In the early
2000's there was a design which was not much more than some penciled scribbles
for something along the lines of logcheck. That program was called GEMS
(Generic Event Management System) and didn't progress past the concept stage.

What accelerated GEMS' demise was a project called Just For Fun Network
Management System or JFFNMS.  This program was written in PHP and combined
the status polling of Nagios with the RRD graphs of cricket and MRTG.  As it
was written in PHP this had all the bonuses and problems of other PHP programs.
It was able to reasonably easily run on Windows and Linux systems, amongst 
others and handled the database and SNMP parts through modules.

Maintaining a PHP program is not easy and tracking down bugs gets very 
difficult.  There needed to be a better way and one solution was to keep
PHP but use a framework such as CakePHP. While this solved some of the framework
problems, it still left PHP with all its quirkyness.

Another series of searches and it was decided to start a completely new
project.  Given it was a rewrite, then there was no need to stay with the same
langauge.  Also the web framework needed to be something reasonably substancial
that took care of things such as database handling, authentication and
web request routing.  In October 2011, Rosenberg NMS was born.

