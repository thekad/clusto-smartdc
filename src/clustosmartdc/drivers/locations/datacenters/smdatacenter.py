#
# -*- mode:python; sh-basic-offset:4; indent-tabs-mode:nil; coding:utf-8 -*-
# vim:set tabstop=4 softtabstop=4 expandtab shiftwidth=4 fileencoding=utf-8:
#

from clusto import exceptions
from clusto.drivers.locations.datacenters import basicdatacenter
import smartdc


class SMDatacenter(basicdatacenter.BasicDatacenter):
    """
    SmartDC Datacenter
    """

    _driver_name = 'smdatacenter'

    def __init__(self, name_driver_entity, **kwargs):

        loc = kwargs.pop('location', name_driver_entity)
        if loc not in smartdc.KNOWN_LOCATIONS:
            raise exceptions.DriverException('This is an unknown location')

        basicdatacenter.BasicDatacenter.__init__(self, name_driver_entity,
            **kwargs)

        self.set_attr(key='smartdc', subkey='location',
            value=loc)

        for k, v in kwargs.items():
            self.set_attr(key='smartdc', subkey=k, value=v)
