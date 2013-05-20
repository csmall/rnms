# -*- coding: utf-8 -*-
#quickstarted Options:
#
# sqlalchemy: True
# auth:       sqlalchemy
# mako:       True
#
#

#This is just a work-around for a Python2.7 issue causing
#interpreter crash at exit when trying to log an info message.
try:
    import logging
    import multiprocessing
except:
    pass

import sys

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

testpkgs=['WebTest >= 1.2.3',
               'nose',
               'coverage',
               'wsgiref',
               'mock',
               ]
install_requires=[
    "TurboGears2 >= 2.2.2",
    "Genshi",
    "Mako",
    "zope.sqlalchemy >= 0.4",
    "repoze.tm2 >= 1.0a5",
    "sqlalchemy<0.8b1",
    "sqlalchemy-migrate",
    "repoze.who",
    "repoze.who-friendlyform >= 1.0.4",
    "tgext.admin >= 0.5.1",
    "repoze.who.plugins.sa",
    "tw2.forms",
    # Rosenberg NMS specific stuff follows
    "tw2.jqplugins.jqgrid",
    "tw2.jqplugins.jqplot",
    "pysnmp",
    "psycopg2",
    "python-rrdtool",
    "mysql-python",
    "pyparsing < 2.0.0",
    "pyzmq"
    ]

setup(
    name='Rosenberg-NMS',
    version='0.0.0',
    description='',
    author='',
    author_email='',
    #url='',
    setup_requires=["PasteScript >= 1.7"],
    paster_plugins=['PasteScript', 'Pylons', 'TurboGears2', 'tg.devtools'],
    packages=find_packages(exclude=['ez_setup']),
    install_requires=install_requires,
    include_package_data=True,
    test_suite='nose.collector',
    tests_require=testpkgs,
    package_data={'rnms': ['i18n/*/LC_MESSAGES/*.mo',
                                 'templates/*/*',
                                 'public/*/*']},
    message_extractors={'rnms': [
            ('**.py', 'python', None),
            ('templates/**.mako', 'mako', None),
            ('public/**', 'ignore', None)]},

    entry_points="""
    [console_scripts]
    rnmsd = rnms.lib.scripts.rnmsd:main
    rnms_adisc = rnms.lib.scripts.att_discovery:main
    rnms_cons = rnms.lib.scripts.consolidate:main
    rnms_info = rnms.lib.scripts.info:main
    rnms_jffimport = rnms.lib.scripts.jffimport:main
    rnms_poller = rnms.lib.scripts.poller:main
    rnms_trapd = rnms.lib.scripts.trapd:main
    rnms_sla = rnms.lib.scripts.sla_analyzer:main

    [paste.app_factory]
    main = rnms.config.middleware:make_app

    [paste.app_install]
    main = pylons.util:PylonsInstaller
    """,
    dependency_links=[
        "http://tg.gy/222"
        ],
    zip_safe=False
)
