Installation
============
There are many ways you can setup RoseNMS.  No single way is "correct"
but there are often pitfalls depending on your particular setup.  This
section describes one way of install RoseNMS.

RoseNMS is basically a WSGI_ interface enabled program.  If you understand
how these sort of programs work, you are free to install RoseNMS any
way you like, using your standard setup.

For the rest of us, I'll assume you have:

* the RoseNMS egg, which contains the program;
* a working apache server with modwsgi installed;
* virtualenv_ which makes virtual environments and dependencies.

There is also three separate directories involved in the installation.
There is absolutely no solid rules where these directories have to go, the
important thing is not to mix them up.

* Baseline - This is where the python interpreter and the system files are
  kept. We will use /usr/local/pythonenv/BASELINE
* RoseNMS environment - Additional packages that RoseNMS needs to run
  will be installed here. This is the location of the specific virtualenv
  we will use. For the document lets call it /usr/local/pythonenv/RoseNMS_NMS
* RoseNMS home - Location of the RoseNMS files, such as a sqlite database
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

RoseNMS Environment
---------------------
The RoseNMS Environment is made almost the same way and will be located
at /usr/local/pythonenv/rnms. It is best to install TurboGears first as
it pulls in the right sort of dependencies, then install RoseNMS.

.. code-block:: bash

  $ cd /usr/local/pythonenv
  $ virtualenv --no-site-packages rnms
  New python executable in rnms/bin/python
  Installing distribute....................................................
  .........................................................................
  .........................................................................
  .....................done.
  Installing pip................done.
  $ source rnms/bin/activate
  (rnms)$ easy_install -i http://tg.gy/current Turbogears2
  (lots of lines of install as things happen!)

  (rnms)$ easy_install /tmp/RoseNMS_NMS-0.0.0dev-py2.7.egg

There will be an awful lot of work going on when you try to install
RoseNMS as easy_install will go off and download all the dependent
packages that are required for RoseNMS to run correctly.

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

.. code-block:: python

    import sys
    prev_sys_path = list(sys.path)
    import site
    site.addsitedir('/usr/local/pythonenv/rnms/lib/python2.7/site-packages')

    new_sys_path = []
    for item in list(sys.path):
        if item not in prev_sys_path:
            new_sys_path.append(item)
            sys.path.remove(item)
    sys.path[:0] = new_sys_path
    #End of virtualenv support

    # This adds your project's root path to the PYTHONPATH so that you can import
    # top-level modules from your project path.  This is how TurboGears QuickStarted
    # projects are laid out by default.
    import os, sys
    sys.path.append('/usr/local/pythonenv/rnms')

    # Set the environment variable PYTHON_EGG_CACHE to an appropriate directory
    # where the Apache user has write permission and into which it can unpack egg files.
    os.environ['PYTHON_EGG_CACHE'] = '/home/rnms/python-eggs'

    # Initialize logging module from your TurboGears config file
    from paste.script.util.logging_config import fileConfig
    fileConfig('/home/rnms/production.ini')

    # Finally, load your application's production.ini file.
    from paste.deploy import loadapp
    application = loadapp('config:/home/rnms/production.ini')

.. _WSGI: http://wsgi.readthedocs.org/
.. _virtualenv: http://www.virtualenv.org/
.. _Virtualenv support for VirtualEnvironments: http://code.google.com/p/modwsgi/wiki/VirtualEnvironments
