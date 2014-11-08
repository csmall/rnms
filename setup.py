# -*- coding: utf-8 -*-
# quickstarted Options:
#
# sqlalchemy: True
# auth:       sqlalchemy
# mako:       True
#
#

# This is just a work-around for a Python2.7 issue causing
# interpreter crash at exit when trying to log an info message.
# try:
#    import logging
#    import multiprocessing
# except:
#    pass


try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

testpkgs = ['WebTest >= 1.2.3',
            'nose',
            'coverage',
            'gearbox',
            'wsgiref',
            'mock',
            ]

install_requires = [
    "TurboGears2 >= 2.3.2",
    "Babel",
    "Genshi",
    "Mako",
    "zope.sqlalchemy >= 0.4",
    "sqlalchemy",
    "alembic",
    "repoze.who",
    "tw2.forms",
    "tgext.admin >= 0.6.1",
    # Rosenberg NMS specific stuff follows
    "tw2.jqplugins.jqgrid",
    "tw2.jqplugins.jqplot",
    "pysnmp",
    "psycopg2",
    "python-rrdtool",
    "mysql-python",
    "pyzmq"
    ]

setup(
    name='Rosenberg-NMS',
    version='0.1',
    description='''\
Rosenberg NMS is a Network Management System which is able to poll your
network equipment such as routers, switches and services. With this
information it can report on device state and graph parameters from the device.
''',
    author='Craig Small',
    author_email='csmall@enc.com.au',
    url='http://rnms.org/',
    packages=find_packages(exclude=['ez_setup']),
    install_requires=install_requires,
    test_suite='nose.collector',
    tests_require=testpkgs,
    package_data={'rnms': ['i18n/*/LC_MESSAGES/*.mo',
                           'templates/*/*',
                           'public/*/*']},
    keywords=[
        'turbogears2.application'
    ],
    message_extractors={'rnms': [
        ('**.py', 'python', None),
        ('templates/**.mako', 'mako', None),
        ('public/**', 'ignore', None)]},

    entry_points={
        'paste.app_factory': [
            'main = rnms.config.middleware:make_app'
        ],
        'gearbox.plugins': [
            'turbogears-devtools = tg.devtools'
        ],
        'console_scripts': [
            'rnms = rnms.command.main:main',
            'rnmsd = rnms.command.daemon.main:main',
            # 'rnmsd = rnms.lib.scripts.rnmsd:main',
        ],
        'rnms.commands': [
            'adisc = rnms.command.att_discover:AdiscCommand',
            'cbackup = rnms.command.config_backup:CbackupCommand',
            'cons = rnms.command.consolidate:ConsCommand',
            'jimport = rnms.command.jffimport:JffnmsImport',
            'list = rnms.command.list:List',
            'poll = rnms.command.poller:PollCommand',
            'sla = rnms.command.sla:Sla',
            'show = rnms.command.show:Show',
            'trapd = rnms.command.trapd:Trapd',
        ],
        'rnmsd.commands': [
            'start = rnms.command.daemon.start:StartCommand',
            'stop = rnms.command.daemon.stop:StopCommand',
        ],
    },
    zip_safe=False
)
