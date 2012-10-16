#!/usr/bin/env python
#
# -*- mode:python; sh-basic-offset:4; indent-tabs-mode:nil; coding:utf-8 -*-
# vim:set tabstop=4 softtabstop=4 expandtab shiftwidth=4 fileencoding=utf-8:
#

from clusto.drivers.base import ResourceManager
from clusto.exceptions import ResourceException
import smartdc


class SMDatacenterManager(ResourceManager):

    _driver_name = 'smdatacentermanager'
    _conns = {}
    _properties = {
        'key_id': None,
    }

    def _connection(self, location, *args, **kwargs):
        """
        Returns a connection "pool" (just a dict with an object per region
        used) to the calling code
        """
        if location not in self._conns:
            self._conns[location] = smartdc.DataCenter(
                location=location,
                key_id=self.key_id,
                **kwargs
            )
        return self._conns[location]

    def allocate(self, thing, resource=(), number=True):
        """
        Makes sure allocate works with only SmartDC objects
        """
        if resource == ():
            return ResourceManager.allocate(self, thing,
                resource=resource, number=number)
        else:
            if not isinstance(resource, smartdc.Machine):
                raise TypeError('You can only allocate Machine resources')
            return ResourceManager.allocate(self, thing,
                resource=resource, number=number)

    def allocator(self, thing, resource=None, number=True):
        """
        This should only be called if you expect a new instance to be
        allocated without .create()
        """
        raise ResourceException('SMDatacenterManager cannot allocate on its '
            'own, needs to be called via .create()')
