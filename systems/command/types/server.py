from settings.roles import Roles
from .router import RouterCommand
from .action import ActionCommand
from systems.command.mixins import network, server, load_balancer


class ServerRouterCommand(RouterCommand):

    def get_priority(self):
        return 35


class ServerActionCommand(
    server.ServerMixin,
    load_balancer.LoadBalancerMixin,
    network.NetworkMixin,
    ActionCommand
):
    def groups_allowed(self):
        return [
            Roles.admin,
            Roles.server_admin
        ]

    def server_enabled(self):
        return True

    def get_priority(self):
        return 40
