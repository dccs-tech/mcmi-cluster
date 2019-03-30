from systems.command import profile


class Provisioner(profile.BaseProvisioner):

    def priority(self):
        return 4

    def ensure(self, name, config):
        provider = self.pop_value('provider', config)
        networks = self.pop_values('network', config)
        subnets = self.pop_values('subnet', config)
        groups = self.pop_values('groups', config)
        firewalls = self.pop_values('firewalls', config)

        if not provider or not networks or not subnets:
            self.command.error("Server {} requires 'provider', 'network', and 'subnet' fields".format(name))

        def process_network(network):
            def process_subnet(subnet):
                self.exec('server save',
                    server_provider_name = provider,
                    server_name = name,
                    server_fields = self.interpolate(config,
                        provider = provider,
                        network = network,
                        subnet = subnet
                    ),
                    network_name = network,
                    subnet_name = subnet,
                    group_names = groups,
                    firewall_names = firewalls
                )
            self.run_list(subnets, process_subnet)
        self.run_list(networks, process_network)

    def scope(self, instance):
        return {
            'network': instance.subnet.network.name,
            'subnet': instance.subnet.name
        }

    def variables(self, instance):
        return {
            'provider': instance.type,
            'groups': self.get_names(instance.groups),
            'firewalls': self.get_names(instance.firewalls)
        }
