Installation
============
There are many ways you can setup Rosenberg.  No single way is "correct"
but there are often pitfalls depending on your particular setup.  This
section describes one way of install Rosenberg.

Rosenberg is basically a WSGI_ interface enabled program.  If you understand
how these sort of programs work, you are free to install Rosenberg any
way you like, using your standard setup.

For the rest of us, I'll assume you have:

* the Rosenberb_NMS egg, which contains the program;
* a working apache server with modwsgi installed;
* virtualenv_ which makes virtual environments and dependencies.

There is also three separate directories involved in the installation.
There is absolutely no solid rules where these directories have to go, the
important thing is not to mix them up.

* Baseline - This is where the python interpreter and the system files are
  kept. We will use /usr/local/pythonenv/BASELINE
* Rosenberg environment - Additional packages that Rosenberg needs to run
  will be installed here. This is the location of the specific virtualenv
  we will use. For the document lets call it /usr/local/pythonenv/Rosenberg_NMS
* Rosenberg home - Location of the Rosenberg files, such as a sqlite database
  or the rrd files, we will use /home/rosenberg

So, now to make the various directories, part of this comes from the
`Virtualenv support for VirtualEnvironments`_ page.

Baseline
--------
.. code-block:: bash

  $ cd /usr/local
  $ mkdir /usr/local/pythonenv
  $ cd /usr/local/pythonenv
  $ virtualenv --no-site-packages BASELINE
  New python executable in BASELINE/bin/python
  Installing distribute....................................................
  .........................................................................
  .........................................................................
  .....................done.
  Installing pip................done.


This directory is where the WSGI server within Apache will find the python
files. You will need to tell it this with a configuration parameter

code-block::
  WSGIPythonHome /usr/local/pythonenv/BASELINE

Rosenberg Environment
---------------------
The Rosenberg Environment is made almost the same way and will be located
at /usr/local/pythonenv/rnms

.. code-block:: bash

  $ cd /usr/local/pythonenv
  $ virtualenv rnms
  New python executable in rnms/bin/python
  Installing distribute....................................................
  .........................................................................
  .........................................................................
  .....................done.
  Installing pip................done.
  $ source rnms/bin/activate
  (rnms)$ easy_install --no-site-packages path./to/RosenbergNMS.egg


There will be an awful lot of work going on when you try to install
Rosenberg as easy_install will go off and download all the dependent
packages that are required for Rosenberg to run correctly.

Apache Configuration
--------------------
The apache configuration shown below basically tells Apache where to 
find the baseline files and where the wsgi file is located. We have
also made 3 WSGI daemons with a name of wsgid. The values given don't
have to be the same but are the defaults seen in most documentation.

.. code-block:: apache

  WSGIPythonHome /usr/local/pythonenv/BASELINE/
  WSGIDaemonProcess example.com threads=10 processes=3 display-name=wsgid
  WSGIProcessGroup example.com
  <VirtualHost *:80>
    ServerName example.com
    WSGIScriptAlias /rnms /home/rosenberg/apache/rnms.wsgi
  </VirtualHost>

WSGI File
---------


.. _WSGI: http://wsgi.readthedocs.org/
.. _virtualenv: http://www.virtualenv.org/
.. _Virtualenv support for VirtualEnvironments: http://code.google.com/p/modwsgi/wiki/VirtualEnvironments
