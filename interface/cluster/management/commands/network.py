from systems.command.base import command_list
from systems.command.factory import resource
from systems.command.types import network


class Command(network.NetworkRouterCommand):

    def get_command_name(self):
        return 'network'

    def get_subcommands(self):
        base_name = self.get_command_name()
        return resource.ResourceCommandSet(
            network.NetworkActionCommand, base_name,
            provider_name = base_name,
            provider_subtype = base_name
        )
