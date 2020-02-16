from django.conf import settings

from data.network.models import Network
from data.subnet.models import Subnet
from systems.plugins import meta, terraform
from utility.data import ensure_list

import netaddr
import ipaddress
import itertools
import threading
import time


class AddressMap(object):

    def __init__(self):
        self.cidr_index = {}
        self.thread_lock = threading.Lock()


    def cidr(self, config):
        with self.thread_lock:
            if 'cidr' in config and config['cidr']:
                cidrs = [self.parse_cidr(config['cidr'])]
            else:
                cidrs = self.parse_subnets(
                    config['cidr_base'],
                    config['cidr_prefix']
                )

            for cidr in cidrs:
                create = True

                for indexed_cidr in self.cidr_index.keys():
                    if self.overlapping_subnets(cidr, indexed_cidr):
                        create = False
                        break

                if create:
                    cidr = str(cidr)
                    self.cidr_index[cidr] = True
                    return cidr

            return None


    def parse_cidr(self, cidr):
        cidr = str(cidr)

        if '*' in cidr or '-' in cidr:
            return netaddr.glob_to_cidrs(cidr)[0]

        if '/' not in cidr:
            cidr = "{}/32".format(cidr)

        return netaddr.IPNetwork(cidr, implicit_prefix = True)

    def parse_subnets(self, cidr, prefix_size):
        return list(self.parse_cidr(str(cidr)).subnet(int(prefix_size)))

    def overlapping_subnets(self, cidr, other_cidr):
        cidr1 = ipaddress.IPv4Network(str(cidr))
        cidr2 = ipaddress.IPv4Network(str(other_cidr))
        return cidr1.overlaps(cidr2)


class NetworkAddressMap(AddressMap):

    def __init__(self):
        super().__init__()

        with self.thread_lock:
            for network in Network.facade.all():
                self.cidr_index[network.cidr] = True


class SubnetAddressMap(AddressMap):

    def __init__(self):
        super().__init__()

        with self.thread_lock:
            for subnet in Subnet.facade.all():
                self.cidr_index[subnet.cidr] = True


class NetworkMixin(object):

    @property
    def address(self):
        return NetworkAddressMap()

class SubnetMixin(object):

    @property
    def address(self):
        return SubnetAddressMap()


class NetworkProvider(NetworkMixin, terraform.TerraformPluginProvider):

    def provider_config(self, type = None):
        self.option(str, 'cidr_base', '10/8', help = 'Network IPv4 root CIDR address (not used if "cidr" option specified)')
        self.option(int, 'cidr_prefix', 16, help = 'Network IPv4 CIDR address prefix size (not used if "cidr" option specified)')

    def terraform_type(self):
        return 'network'

    def store_lock_id(self):
        return 'terraform-network-provider'

    @property
    def facade(self):
        return self.command._network

    def initialize_terraform(self, instance, created):
        if not instance.cidr:
            instance.cidr = self.address.cidr(self.config)

        if not instance.cidr:
            self.command.error("No available network cidr matches. Try another cidr")


class SubnetProvider(SubnetMixin, terraform.TerraformPluginProvider):

    def provider_config(self, type = None):
        self.option(int, 'cidr_prefix', 24, help = 'Subnet IPv4 CIDR address prefix size (not used if "cidr" option specified)')

    def terraform_type(self):
        return 'subnet'

    def store_lock_id(self):
        return 'terraform-network-provider'

    @property
    def facade(self):
        return self.command._subnet

    def initialize_terraform(self, instance, created):
        self.config['cidr_base'] = instance.network.cidr

        if not instance.cidr:
            instance.cidr = self.address.cidr(self.config)

        if not instance.cidr:
            self.command.error("No available subnet cidr matches. Try another cidr")


class FirewallProvider(terraform.TerraformPluginProvider):

    def terraform_type(self):
        return 'firewall'

    @property
    def facade(self):
        return self.command._firewall

    def get_firewall_id(self):
        return self.instance.id


class FirewallRuleProvider(NetworkMixin, terraform.TerraformPluginProvider):

    def provider_config(self, type = None):
        self.option(bool, 'self_only', False, help = 'Only allow access from other infrastructure resources attached to this firewall')
        self.option(str, 'source_firewall', None, help = 'Only allow access from other infrastructure resources attached to another firewall')

    def terraform_type(self):
        return 'firewall_rule'

    @property
    def facade(self):
        return self.command._firewall_rule

    def initialize_terraform(self, instance, created):
        instance.config['rule_type'] = 'cidr'
        instance.config['source_firewall_id'] = None

        if instance.config['source_firewall']:
            instance.config['rule_type'] = 'link'
            instance.config['self_only'] = False
            instance.cidrs = []
            tries = 60

            while True:
                firewall = self.command._firewall.retrieve(instance.config['source_firewall'])
                if firewall:
                    firewall.initialize(self.command)
                    instance.config['source_firewall_id'] = firewall.provider.get_firewall_id()
                    break
                time.sleep(2)
                tries -= 2
                if not tries:
                    self.command.error("Source firewall {} could not be retrieved".format(instance.config['source_firewall']))

        elif instance.config['self_only']:
            instance.config['rule_type'] = 'link'
            instance.cidrs = []

        elif instance.cidrs:
            instance.cidrs = [str(self.address.parse_cidr(x.strip())) for x in ensure_list(instance.cidrs)]

        elif not instance.config['self_only'] and not instance.config['source_firewall']:
            instance.cidrs = ['0.0.0.0/0']


class BaseProvider(meta.MetaPluginProvider):

    def register_types(self):
        self.set('network', NetworkProvider)
        self.set('subnet', SubnetProvider)
        self.set('firewall', FirewallProvider)
        self.set('firewall_rule', FirewallRuleProvider)
