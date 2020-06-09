from systems.plugins.index import BasePlugin
from utility.data import ensure_list


class LoadBalancerProvider(BasePlugin('load_balancer.load_balancer')):

    def prepare_instance(self, instance, created):
        super().prepare_instance(instance, created)
        self.update_domain_reference(instance)

    def finalize_terraform(self, instance):
        self.remove_domain_reference(instance)
        super().finalize_terraform(instance)


    def update_domain_reference(self, instance):
        if instance.domain:
            dns_name = instance.variables['lb_dns_name']
            domain_target = "{}.{}".format(
                instance.name,
                instance.domain.name
            )
            domain_name = "{}-{}".format(domain_target, dns_name)

            record = self.command._domain_record.retrieve(
                domain_name,
                domain = instance.domain
            )
            if not record:
                provider = self.command.get_provider(
                    self.command._domain_record.meta.provider_name,
                    instance.domain.provider_type
                )
                record = provider.create(domain_name, {
                    'domain': instance.domain,
                    'target': domain_target,
                    'type': 'CNAME',
                    'values': [ dns_name ]
                })
            else:
                record.initialize(self.command)
                record.provider.update()

    def remove_domain_reference(self, instance):
        if instance.domain:
            dns_name = instance.variables['lb_dns_name']
            domain_target = "{}.{}".format(
                instance.name,
                instance.domain.name
            )
            domain_name = "{}-{}".format(domain_target, dns_name)

            record = self.command._domain_record.retrieve(
                domain_name,
                domain = instance.domain
            )
            if record:
                record.initialize(self.command)
                record.provider.delete()


class LoadBalancerListenerProvider(BasePlugin('load_balancer.load_balancer_listener')):

    def initialize_terraform(self, instance, created):
        super().initialize_terraform(instance, created)
        instance.healthy_status = ensure_list(instance.healthy_status)
