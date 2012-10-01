#
# -*- mode:python; sh-basic-offset:4; indent-tabs-mode:nil; coding:utf-8 -*-
# vim:set tabstop=4 softtabstop=4 expandtab shiftwidth=4 fileencoding=utf-8:
#

from clusto import exceptions
from clusto.drivers.devices.servers import BasicVirtualServer
from clustosmartdc.drivers.locations.datacenters import smdatacenter


class SMVirtualServer(BasicVirtualServer):

    _driver_name = 'smserver'
    _port_meta = {}
    _sm = None

    @property
    def _instance(self):
        "Returns a smartdc.Machine instance to work with"

        if not self._sm:
            p = self.parents(clusto_drivers=[smdatacenter.SMDatacenter])
            if not p:
                raise exceptions.ResourceException('A smartdc datacenter '
                    'is not parent of this server')
            p = p.pop()

            sdc = p.get_sdc()
            self._sm = sdc.machine(self.attr_value(key='smartdc',
                subkey='machine_id'))

        return self._sm

    @property
    def state(self):
        "Get the instance state."

        self._instance.refresh()
        return self._instance.state

    def console(self, *args, **kwargs):
        raise NotImplementedError

    def update_metadata(self, *args, **kwargs):
        "Updates the metadata information from the provider"

        self.clear_metadata()

#       Update the ip addresses
        for ip in self._instance.private_ips:
            self.add_attr(key='ip', subkey='nic-eth', value=ip)
        for ip in self._instance.public_ips:
            self.set_attr(key='ip', subkey='ext-eth', value=ip)

#       Update system attributes
        self.set_attr(key='system', subkey='memory',
            value=self._instance.memory)
        self.set_attr(key='system', subkey='disk',
            value=self._instance.disk)

    def clear_metadata(self, *args, **kwargs):
        "Clears the metadata previously fetched from the provider"
        self.del_attrs('ip')
        self.del_attrs('system')

    def shutdown(self, captcha=True, wait=False):
        if captcha and not self._power_captcha('shutdown'):
            return False
        self._instance.stop()
        if wait:
            self._instance.poll_until('stopped')

    def start(self, captcha=False, wait=False):
        if captcha and not self._power_captcha('start'):
            return False
        self._instance.start()
        if wait:
            self._instance.poll_until('running')

    def reboot(self, captcha=True):
        if captcha and not self._power_captcha('reboot'):
            return False
        self._instance.reboot()

    def create(self, captcha=False, wait=False):

        p = self.parents(clusto_drivers=[smdatacenter.SMDatacenter])
        if not p:
            raise exceptions.ResourceException('A smartdc datacenter '
                'is not parent of this server')
        p = p.pop()

        sdc = p.get_sdc()

        kwargs = {
            'name': self.name,
        }
        boot_script = self.attr_value(key='smartdc', subkey='boot_script',
            merge_container_attrs=True)
        package = self.attr_value(key='smartdc', subkey='package',
            merge_container_attrs=True)
        dataset = self.attr_value(key='smartdc', subkey='dataset',
            merge_container_attrs=True)

        if boot_script:
            kwargs['boot_script'] = boot_script
        if package:
            kwargs['package'] = package
        if dataset:
            kwargs['dataset'] = dataset

        self._sm = sdc.create_machine(**kwargs)

        if wait:
            self._instance.poll_until('running')

        self.set_attr(key='smartdc', subkey='machine_id',
            value=self._sm.id)

    def destroy(self, captcha=True, wait=False):
        if captcha and not self._power_captcha('destroy'):
            return False
        self._instance.stop()
        if wait:
            self._instance.poll_until('stopped')
        self._instance.delete()
        self.clear_metadata()
        self.entity.delete()
