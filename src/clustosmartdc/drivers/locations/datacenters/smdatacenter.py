#
# -*- mode:python; sh-basic-offset:4; indent-tabs-mode:nil; coding:utf-8 -*-
# vim:set tabstop=4 softtabstop=4 expandtab shiftwidth=4 fileencoding=utf-8:
#

from clusto import exceptions
from clusto.drivers.locations.datacenters import basicdatacenter
from smartdc import datacenter as sm_datacenter


class SMDatacenter(basicdatacenter.BasicDatacenter):
    """
    SmartDC Datacenter
    """

    _driver_name = 'smdatacenter'
    _dc = None

    def __init__(self, name_driver_entity, **kwargs):

        if 'key_id' not in kwargs:
            raise exceptions.DriverException('Need a key_id')

        basicdatacenter.BasicDatacenter.__init__(self, name_driver_entity,
            **kwargs)

        key = kwargs.pop('key_id')
        loc = kwargs.pop('location', name_driver_entity)

        self.set_attr(key='smartdc', subkey='location',
            value=loc)
        self.set_attr(key='smartdc', subkey='key_id',
            value=key)

        self._dc = sm_datacenter.DataCenter(location=loc, key_id=key, **kwargs)
        for k, v in kwargs.items():
            self.set_attr(key='smartdc', subkey=k, value=v)

    @property
    def _datacenter(self):
        "Returns a smartdc.DataCenter instance to work with"

        if not self._dc:
            kwargs = {}
            for attr in self.attrs(key='smartdc'):
                kwargs[attr.subkey] = attr.value
            self._dc = sm_datacenter.DataCenter(**kwargs)
        return self._dc
