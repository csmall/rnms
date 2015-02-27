# -*- coding: utf-8 -*-
#
# This file is part of the RoseNMS
#
# Copyright (C) 2011-2015 Craig Small <csmall@enc.com.au>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <http://www.gnu.org/licenses/>
#
""" Test suite for the Host model in RoseNMS"""
from nose.tools import eq_

from rnms import model
from rnms.tests.models import ModelTest


# Needed for a zone
class TestZone(ModelTest):
    klass = model.Zone
    attrs = dict(
        display_name=u'Test Zone',
        short_name=u'test'
        )


class TestHost(ModelTest):
    klass = model.Host
    attrs = dict(
        mgmt_address='127.0.0.1',
        display_name='localhost',
        )

    def test_host_by_address(self):
        """Host can correctly be fetched by management address"""
        new_host = model.Host.by_address('127.0.0.1')
        eq_(new_host, self.obj)

    def test_host_blank_attribute(self):
        """Host returns none for blank attribute"""
        attrib = self.obj.attrib_by_index('blank')
        eq_(attrib, None)


class TestIface(ModelTest):
    klass = model.Iface
    attrs = dict(
            ifindex=42,
            display_name = u'lo0',
            iftype = 4
            )

    def test_iface_init_ifindex(self):
        """Iface init sets ifindex correctly"""
        eq_(self.obj.ifindex,42) 

    def test_iface_init_iftype(self):
        """Iface init sets iftype correctly"""
        eq_(self.obj.iftype,4) 

    def test_iface_init_display_name(self):
        """Iface init sets display_name correctly"""
        eq_(self.obj.display_name,u'lo0') 

class TestConfigBackupMethod(ModelTest):
    klass = model.ConfigBackupMethod
    attrs = dict(
            display_name = u'Test ConfigBackupMethod',
            plugin_name = 'testct'
            )
    def test_ct_init_display_name(self):
        """ConfigBackupMethod init sets display_name correctly"""
        eq_(self.obj.display_name, u'Test ConfigBackupMethod')

    def test_ct_init_plugin_name(self):
        """ConfigBackupMethod init sets plugin_name correctly"""
        eq_(self.obj.plugin_name,'testct') 

class TestHostConfig(ModelTest):
    klass = model.HostConfig
    attrs = dict(
           config = 'test config'
            )
    def do_get_dependencies(self):
        host = model.Host(display_name=u'Test Host')
        return{'host': host}

    def test_config_init_config(self):
        """HostConfig init sets config string correctly"""
        eq_(self.obj.config, 'test config') 

