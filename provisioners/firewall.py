from systems.command import profile


class Provisioner(profile.BaseProvisioner):

    def priority(self):
        return 3

    def ensure(self, name, config):
        networks = self.pop_values('network', config)
        rules = self.pop_info('rules', config)
        groups = self.pop_values('groups', config)

        if not networks or not rules:
            self.command.error("Firewall {} requires 'network' and 'rules' fields".format(name))

        def process_network(network):
            self.exec('firewall save',
                firewall_name = name,
                firewall_fields = self.interpolate(config,
                    network = network
                ),
                network_name = network,
                group_names = groups,
                test = self.test
            )
            def process_rule(rule):
                self.exec('firewall rule save',
                    firewall_rule_name = rule,
                    firewall_rule_fields = self.interpolate(rules[rule],
                        network = network,
                        firewall = name
                    ),
                    network_name = network,
                    firewall_name = name,
                    test = self.test
                )
            self.run_list(rules.keys(), process_rule)
        self.run_list(networks, process_network)

    def scope(self, instance):
        return { 'network': instance.network.name }

    def variables(self, instance):
        variables = {
            'groups': self.get_names(instance.groups),
            'rules': {}
        }
        for rule in instance.firewallrule_relation.all():
            variables['rules'][rule.name] = self.get_variables(rule)

        return variables
