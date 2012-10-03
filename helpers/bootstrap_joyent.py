#!/usr/bin/env python
#
# -*- mode:python; sh-basic-offset:4; indent-tabs-mode:nil; coding:utf-8 -*-
# vim:set tabstop=4 softtabstop=4 expandtab shiftwidth=4 fileencoding=utf-8:
#

import sys

import clusto
from clusto import script_helper
from clusto import drivers
from clustosmartdc.drivers.locations import smdatacenter
from clustosmartdc.drivers.devices.servers import smserver
import smartdc


class BootstrapJoyent(script_helper.Script):
    """
    Will bootstrap your ec2 infrastructure (regions, zones, etc)
    """

    def __init__(self):
        script_helper.Script.__init__(self)

    def _add_arguments(self, parser):
        parser.add_argument('--add-to-pool', '-p', default=None,
            help='If given, joyent "location" objects will be inserted in '
                'the given pool')
        parser.add_argument('--secret', '-s', default=None,
            help='The SSH private key file')
        parser.add_argument('--no-ssh-agent', default=False,
            action='store_true', help='If you do not want to use '
            'SSH agent auth')
        parser.add_argument('key_id', nargs=1, type=str,
            help='The target key be used (i.e. /user@domain.com/keys/foo)')

    def add_subparser(self, subparsers):
        parser = self._setup_subparser(subparsers)
        self._add_arguments(parser)

    def run(self, args):
        self.info('Creating known joyent locations and importing '
            'existing machines')
        key = args.key_id.pop()

        p = None
        if args.add_to_pool:
            p = clusto.get_or_create(args.add_to_pool, drivers.pool.Pool)

        for loc, url in smartdc.KNOWN_LOCATIONS.items():
            self.debug('Creating location %s' % (loc,))
            sdc = clusto.get_or_create(loc, smdatacenter.SMDatacenter,
                key_id=key, location=loc)
            if p and sdc not in p:
                p.insert(sdc)
            self.debug('Testing connectivity to %s' % (loc,))
            try:
                machines = sdc._datacenter.machines()
                self.debug('Number of existing machines: %d' %
                    (len(machines),))
            except Exception as e:
                self.warn(e)
                self.error('Your credentials seem to be incorrect for %s' %
                    (loc,))
                continue
            for machine in machines:
                self.debug('Getting/creating clusto object for %s' %
                    (machine))
                n = clusto.get_or_create(machine.name,
                    smserver.SMVirtualServer, machine_id=machine.id)
                if n not in sdc:
                    sdc.insert(n)
                n.update_metadata()
        self.info('Done.')


def main():
    bootstrap, args = script_helper.init_arguments(BootstrapJoyent)
    return(bootstrap.run(args))

if __name__ == '__main__':
    sys.exit(main())
