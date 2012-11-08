# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


from django.test import TestCase

from ralph.discovery.models import DeviceType, Device
from ralph.discovery.models_history import HistoryChange


class ModelsTest(TestCase):
    def test_device_create_empty(self):
        with self.assertRaises(ValueError):
            Device.create(model_name='xxx', model_type=DeviceType.unknown)

    def test_device_create_nomodel(self):
        with self.assertRaises(ValueError):
            Device.create(sn='xxx')

    def test_device_conflict(self):
        Device.create([('1', 'DEADBEEFCAFE', 0)],
                      model_name='xxx', model_type=DeviceType.rack_server)
        Device.create([('1', 'CAFEDEADBEEF', 0)],
                      model_name='xxx', model_type=DeviceType.rack_server)
        with self.assertRaises(ValueError):
            Device.create([('1', 'DEADBEEFCAFE', 0), ('2', 'CAFEDEADBEEF', 0)],
                          model_name='yyy', model_type=DeviceType.switch)

    def test_device_create_blacklist(self):
        ethernets = [
            ('1', 'DEADBEEFCAFE', 0),
            ('2', 'DEAD2CEFCAFE', 0),
        ]
        dev = Device.create(ethernets, sn='None',
                            model_name='xxx', model_type=DeviceType.unknown)

        self.assertEqual(dev.sn, None)
        macs = [e.mac for e in dev.ethernet_set.all()]
        self.assertEqual(macs, ['DEADBEEFCAFE'])

    def test_device_history(self):
        dev = Device.create(
            model_name='xxx',
            model_type=DeviceType.unknown,
            sn='xaxaxa',
            user='ralph',
        )
        dev.name = 'dev1'
        dev.save()
        history = HistoryChange.objects.all()
        self.assertEqual(history[0].field_name, 'id')
        self.assertEqual(history[0].new_value, '1')
        self.assertEqual(history[1].old_value, '')
        self.assertEqual(history[1].new_value, dev.name)
