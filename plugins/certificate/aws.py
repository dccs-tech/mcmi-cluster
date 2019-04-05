from utility.cloud.aws import AWSServiceMixin
from .base import BaseProvider


class Provider(AWSServiceMixin, BaseProvider):

    def initialize_terraform(self, instance, created):
        self.aws_credentials(instance.config)
        super().initialize_terraform(instance, created)

    def prepare_instance(self, instance, created):
        super().prepare_instance(instance, created)
        self.clean_aws_credentials(instance.config)

    def finalize_terraform(self, instance):
        self.aws_credentials(instance.config)
        super().finalize_terraform(instance)
