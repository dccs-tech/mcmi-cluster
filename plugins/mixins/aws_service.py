from systems.plugins.index import ProviderMixin
from utility.data import ensure_list

import os
import boto3


class AWSServiceMixin(ProviderMixin('aws_service')):

    @classmethod
    def generate(cls, plugin, generator):
        super().generate(plugin, generator)

        def add_credentials(self, config):
            self.aws_credentials(config)

        def remove_credentials(self, config):
            self.clean_aws_credentials(config)

        plugin.add_credentials = add_credentials
        plugin.remove_credentials = remove_credentials


    def aws_credentials(self, config):
        try:
            config['access_key'] = self.command.get_config('aws_access_key', required = True).strip()
            os.environ['AWS_ACCESS_KEY_ID'] = config['access_key']

            config['secret_key'] = self.command.get_config('aws_secret_key', required = True).strip()
            os.environ['AWS_SECRET_ACCESS_KEY'] = config['secret_key']

        except Exception:
            self.command.error("To use AWS provider you must have 'aws_access_key' and 'aws_secret_key' environment configurations; see: config save")

        return config

    def clean_aws_credentials(self, config):
        config.pop('access_key', None)
        os.environ.pop('AWS_ACCESS_KEY_ID', None)

        config.pop('secret_key', None)
        os.environ.pop('AWS_SECRET_ACCESS_KEY', None)


    def _init_aws_session(self):
        if not getattr(self, 'session', None):
            config = self.aws_credentials({})
            self.session = boto3.Session(
                aws_access_key_id = config['access_key'],
                aws_secret_access_key = config['secret_key']
            )

    def ec2(self, network):
        self._init_aws_session()
        return self.session.client('ec2',
            region_name = network.config['region']
        )

    def efs(self, network):
        self._init_aws_session()
        return self.session.client('efs',
            region_name = network.config['region']
        )
