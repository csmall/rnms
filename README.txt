                          README for RoseNMS

Installation and Setup
======================

Install ``RoseNMS`` using the setup.py script::

    $ cd RoseNMS
    $ python setup.py develop

Create the project database for any model classes defined::

    $ gearbox setup-app

Optionally, if you need to import the JFFNMS configuration in::

    $ rnms jimport -c development.ini
rnms will use /etc/jffnms for the configuration directory, add the
option --jconf <your dir> for a different location.

Start the paste http server::

    $ gearbox serve

While developing you may want the server to reload after changes in package files (or its dependencies) are saved. This can be achieved easily by adding the --reload option::

    $ gearbox serve --reload --debug

Then you are ready to go.
