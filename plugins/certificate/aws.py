from systems.plugins.index import BaseProvider


class Provider(BaseProvider('certificate', 'aws')):

    def add_credentials(self, config):
        self.aws_credentials(config)

    def remove_credentials(self, config):
        self.clean_aws_credentials(config)
