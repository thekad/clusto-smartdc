#
# -*- mode:python; sh-basic-offset:4; indent-tabs-mode:nil; coding:utf-8 -*-
# vim:set tabstop=4 softtabstop=4 expandtab shiftwidth=4 fileencoding=utf-8:
#

from clusto import exceptions
from clusto.drivers.devices.servers import BasicVirtualServer
from clustosmartdc.drivers.resourcemanagers import smdatacentermanager
import IPy


class SMVirtualServer(BasicVirtualServer):

    _driver_name = 'smserver'
    _port_meta = {}
    _sm = None
    _int_ip_const = 2147483648

    def _int_to_ipy(self, num):
        return IPy.IP(num + self._int_ip_const)

    def __init__(self, name_driver_entity, **kwargs):

        BasicVirtualServer.__init__(self, name_driver_entity,
            **kwargs)

        mid = kwargs.pop('machine_id', None)

        if mid:
            self.set_attr(key='smartdc', subkey='machine_id', value=mid)

        for k, v in kwargs.items():
            self.set_attr(key='smartdc', subkey=k, value=v)

    @property
    def _instance(self):
        "Returns a smartdc.Machine instance to work with"

        if not self._sm:
            machine_data = self.attr_value(key='smdcmanager',
                subkey='machine')
            if not machine_data:
                return None
            machine_id = machine_data.get('id')
            if not machine_id:
                return None

            res = smdatacentermanager.SMDatacenterManager.resources(self)[0]
            dcman = smdatacentermanager.SMDatacenterManager.\
                get_resource_manager(res)

            location = res.value.get('location')
            self._sm = dcman._connection(location).machine(machine_id)

        return self._sm

    @property
    def state(self):
        "Get the instance state."

        self._instance.refresh()
        return self._instance.state

    def console(self, *args, **kwargs):
        raise NotImplementedError('No console access on this device')

    def update_metadata(self, *args, **kwargs):
        "Updates the metadata information from the provider"

        self.clear_metadata()

#       Update the ip addresses
        for ip in self._instance.private_ips:
            self.add_attr(key='ip', subkey='nic-eth',
                value=IPy.IP(ip).int())
        for ip in self._instance.public_ips:
            self.set_attr(key='ip', subkey='ext-eth',
                value=IPy.IP(ip).int())

#       Update system attributes
        self.set_attr(key='system', subkey='memory',
            value=self._instance.memory)
        self.set_attr(key='system', subkey='disk',
            value=self._instance.disk)

#       Update the smartdc metadata
        m = self._instance.metadata
        'root_authorized_keys' in m and m.pop('root_authorized_keys')
        if m:
            self.set_attr(key='smartdc', subkey='metadata', value=m)

    def clear_metadata(self, *args, **kwargs):
        "Clears the metadata previously fetched from the provider"
        self.del_attrs('ip')
        self.del_attrs('system')

    def power_off(self, captcha=True, wait=False):
        "Stops the instance is it's running"

        if self.state == 'running':
            if captcha and not self._power_captcha('shutdown'):
                return False
            self._instance.stop()
            if wait:
                self._instance.poll_until('stopped')

        return self._instance.state

    def power_on(self, captcha=False, wait=False):
        "Starts the instance if it's stopped"

        if self.state == 'stopped':
            if captcha and not self._power_captcha('start'):
                return False
            self._instance.start()
            if wait:
                self._instance.poll_until('running')

        return self._instance.state

    def power_reboot(self, captcha=True):
        "Reboots the instance if it's running"

        if self.state == 'running':
            if captcha and not self._power_captcha('reboot'):
                return False
            self._instance.reboot()

        return self.state

    def create(self, captcha=False, wait=False):

        if self._sm:
            raise exceptions.ResourceException(
                'This instance is already created')

        res = smdatacentermanager.SMDatacenterManager.resources(self)[0]
        mgr = smdatacentermanager.SMDatacenterManager.get_resource_manager(res)

        location = res.value.get('location')

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
        elif mgr._connection(location).default_package():
            kwargs['package'] = mgr._connection(location).\
                default_package()['name']
        else:
            raise ValueError('Need a package to create this instance')

        if dataset:
            kwargs['dataset'] = dataset
        elif mgr._connection(location).default_dataset():
            kwargs['dataset'] = mgr._connection(location).\
                default_dataset()['urn']
        else:
            raise ValueError('Need a dataset to create this instance')

        self._sm = mgr._connection(location).create_machine(**kwargs)

        if wait:
            self._instance.poll_until('running')

        result = mgr.additional_attrs(self, resource={'machine': self._sm})

        return (result, True)

    def destroy(self, captcha=True, wait=False):
        if captcha and not self._power_captcha('destroy'):
            return False
        if self.state == 'running':
            self._instance.stop()
            if wait:
                self._instance.poll_until('stopped')
        self._instance.delete()
        self.clear_metadata()
        self.entity.delete()

    def get_ips(self, objects=False):
        """
        Returns a list of IP addresses to work with. Alternatively,
        it can return a list of IPy.IP objects.
        """
        ips = []
        l = self.attr_values(key='ip', subkey='nic-eth')
        if l:
            if objects:
                [ips.append(self._int_to_ipy(_)) for _ in l]
            else:
                [ips.append(self._int_to_ipy(_).strNormal()) for _ in l]
        l = self.attr_values(key='ip', subkey='ext-eth')
        if l:
            if objects:
                [ips.append(self._int_to_ipy(_)) for _ in l]
            else:
                [ips.append(self._int_to_ipy(_).strNormal()) for _ in l]
        return ips
