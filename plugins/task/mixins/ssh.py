
class SSHTaskMixin(object):

    def _ssh_servers(self, params):
        return self.command.search_instances(
            self.manager.get_facade_index()['server'],
            queries = params.get('servers', []),
            joiner = params.get('filter', 'AND').upper(),
            error_on_empty = False
        )

    def _ssh_exec(self, server, command, args = None, options = None, env = None, sudo = False, ssh = None):
        if not args:
            args = []
        if not options:
            options = {}
        if not env:
            env = {}

        if not ssh:
            ssh = server.provider.ssh(env = env)

        if sudo:
            ssh.sudo(command, *args, **options)
        else:
            ssh.exec(command, *args, **options)

