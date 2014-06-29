Rosenberg NMS
=============
Rosenberg NMS (rnms) is, as the name implies, a Network Management System.
What this means is rnms is a piece of software that gathers information
on devices out on a network and tries to meaningfully interpret them to 
make monitoring and managment simpler.

rnms is written in python and is based upon the Turbogears 2 web framework.
The basic concept is largely built around the ideas that were put into
another NMS program called JFFNMS.

The project is based upon [TurboGears](http://turbogears.org) which means
it has the same strengths as that project. That means you have a wide
variety of databases that are supported and the modern framework should
look better, or it will later.

Current Status
--------------

This software is currently at a **pre Alpha** stage.  While it might work
you, it is more likely to break in strange and interesting ways.  Strange for
you, interesting for me because I have another fix.

It currently imports a JFFNMS database and will run the pollers and
consolidators you'd expect.  A lot of the graphs types are missing but are
being added pretty regularly.  Config transfers are not there yet.

Download it and try it out, just don't depend on it to keep your monitoring 
going.  I've recently also had (and fixed) a bug that took the program to 
100% CPU so you've been warned.

The Admin screens are the Turbogears default largely which means they're
about as useful as a database dump.

Installation
------------
apt-get install python-dev libzmq3-dev libmysqlclient-dev librrd-dev libpq-dev
