from systems.plugins.index import BaseProvider
from utility.data import ensure_list

import os


class Provider(BaseProvider('task', 'remote_script')):

    def execute(self, results, params):
        script_path = self.get_path(self.field_script)

        if not os.path.exists(script_path):
            self.command.error("Remote script task provider file {} does not exist".format(script_path))

        script_base, script_ext = os.path.splitext(script_path)
        temp_path = "/tmp/{}{}".format(self.generate_name(24), script_ext)

        env = self._env_vars(params)
        options = self._merge_options(self.field_options, params, self.field_lock)
        args = ensure_list(self.field_args, []))
        sudo = self.field_sudo

        def exec_server(server):
            ssh = server.provider.ssh(env = env)
            ssh.upload(script_path, temp_path, mode = 755)
            try:
                self._ssh_exec(server, temp_path,
                    self._interpolate(args, options),
                    sudo = sudo,
                    env = env,
                    ssh = ssh
                )
            finally:
                ssh.sudo('rm -f', temp_path)

        self.command.run_list(
            self._ssh_servers(params),
            exec_server
        )
