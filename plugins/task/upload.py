from .base import BaseProvider
from .mixins import cli, ssh

import os


class Provider(
    cli.CLITaskMixin,
    ssh.SSHTaskMixin,
    BaseProvider
):
    def execute(self, results, params):
        if 'file' in self.config:
            file_path = self.get_path(self.config['file'])
        else:
            self.command.error("Upload task provider must have a 'file' property specified that links to an existing file")

        if not os.path.exists(file_path):
            self.command.error("Upload task provider file {} does not exist".format(file_path))

        if 'remote_path' not in self.config:
            self.command.error("Upload task provider must have a 'remote_path' property specified that links to an existing file")

        if 'mode' not in self.config:
            self.config['mode'] = 0o644

        def exec_server(server):
            ssh = server.provider.ssh()
            ssh.upload(file_path, self.config['remote_path'],
                mode = self.config['mode'],
                owner = self.config.get('owner', None),
                group = self.config.get('group', None)
            )

        self.command.run_list(
            self._ssh_servers(params),
            exec_server
        )
