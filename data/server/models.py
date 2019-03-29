from django.db import models as django

from settings.roles import Roles
from systems.models import fields, subnet, firewall, provider, group


class ServerFacade(
    provider.ProviderModelFacadeMixin,
    group.GroupModelFacadeMixin,
    subnet.SubnetModelFacadeMixin
):
    def get_field_public_ip_display(self, instance, value, short):
        return value

    def get_field_private_ip_display(self, instance, value, short):
        return value

    def get_field_user_display(self, instance, value, short):
        return value

    def get_field_password_display(self, instance, value, short):
        if short:
            return '*****' if value else None
        return value

    def get_field_private_key_display(self, instance, value, short):
        if short:
            return '*****' if value else None
        return value

    def get_field_data_device_display(self, instance, value, short):
        return value

    def get_field_backup_device_display(self, instance, value, short):
        return value

    def get_field_status_display(self, instance, value, short):
        return self.model.STATUS_RUNNING if self.ping() else self.model.STATUS_UNREACHABLE

    def ping(self, port = 22):
        return self.model.provider.ping(port = port)


class Server(
    provider.ProviderMixin,
    group.GroupMixin,
    firewall.FirewallRelationMixin,
    subnet.SubnetModel
):
    public_ip = django.CharField(null = True, max_length = 128)
    private_ip = django.CharField(null = True, max_length = 128)
    user = django.CharField(null = True, max_length = 128)
    password = fields.EncryptedCharField(null = True, max_length = 1096)
    private_key = fields.EncryptedDataField(null = True)
    data_device = django.CharField(null = True, max_length = 256)
    backup_device = django.CharField(null = True, max_length = 256)

    class Meta(subnet.SubnetModel.Meta):
        verbose_name = "server"
        verbose_name_plural = "servers"
        facade_class = ServerFacade
        ordering = ['name']
        provider_name = 'server'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.STATUS_RUNNING = 'running'
        self.STATUS_UNREACHABLE = 'unreachable'

    def __str__(self):
        return "{} ({})".format(self.name, self.ip)

    @property
    def ip(self):
        return self.public_ip if self.public_ip else self.private_ip


    def allowed_groups(self):
        return [ Roles.admin, Roles.server_admin ]

    def running(self):
        if self.status == self.STATUS_RUNNING:
            return True
        return False
