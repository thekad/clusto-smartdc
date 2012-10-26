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
    _attr_name = 'smdcmanager'
    _conns = {}
    _properties = {
        'key_id': None,
    }

    def _connection(self, location, *args, **kwargs):
        """
        Returns a connection "pool" (just a dict with an object per location 
        used) to the calling code
        """
        if location not in self._conns:
            self._conns[location] = smartdc.DataCenter(
                location=location,
                key_id=self.key_id,
                **kwargs
            )
        return self._conns[location]

    def _connection_to_dict(self, connection):
        """
        Return a dict representation of the connection
        """

        data = connection.me()
        data.update({'location': connection.location})
        return data

    def _machine_to_dict(self, machine):
        """
        Return a dict representation of the machine data
        """

        data = {
            'id': machine.id,
            'name': machine.name,
            'created': str(machine.created),
        }

        return data

    def additional_attrs(self, thing, resource, number=True):
        """
        Record the image allocation as additional resource attrs
        """

        for name, val in resource.items():
            if isinstance(val, smartdc.machine.Machine):
                data = self._machine_to_dict(val)
                self.set_resource_attr(thing,
                    resource,
                    number=number,
                    key=name,
                    value=data
                )
                return data

    def allocator(self, thing, resource=None, number=True):
        """
        Allocate a new datacenter connection to a given thing
        """

        for res in self.resources(thing):
            raise ResourceException("%s is already assigned to %s"
                % (thing.name, res.value))

        location = thing.attr_value(key='smartdc', subkey='location',
            merge_container_attrs=True)

        if not location:
            raise ValueError('%s has to belong to a location before '
                'allocating' % (thing.name,))

        return (self._connection_to_dict(self._connection(location)), True)
