from settings.roles import Roles
from .router import RouterCommand
from .action import ActionCommand
from systems.command import mixins


class StorageRouterCommand(RouterCommand):

    def get_priority(self):
        return 45


class StorageActionCommand(
    mixins.StorageMixin,
    mixins.NetworkMixin,
    ActionCommand
):
    def groups_allowed(self):
        return [
            Roles.admin,
            Roles.storage_admin
        ]

    def server_enabled(self):
        return True

    def get_priority(self):
        return 45
