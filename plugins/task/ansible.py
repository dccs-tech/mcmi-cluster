from django.conf import settings

from systems.plugins.index import BaseProvider
from utility.runtime import Runtime
from utility.temp import temp_dir
from utility.data import clean_dict, ensure_list

import os
import re
import json
import threading


class AnsibleInventory(object):

    def __init__(self, provider, servers, temp):
        self.temp = temp

        self.provider = provider
        self.servers = servers
        self.hosts = []
        self.groups = {}

        self.generate_hosts()
        self.group_servers()


    def get_server_id(self, server):
        return "{}-{}".format(server.name.replace('_', '-'), server.ip)


    def generate_hosts(self):
        self.hosts = []

        for index, server in enumerate(self.servers):
            host = clean_dict({
                'server': server,
                'server_index': index + 1,
                'server_private_ip': server.private_ip,
                'server_public_ip': server.public_ip,
                'ansible_host': server.ip,
                'ansible_port': server.ssh_port,
                'ansible_user': server.user,
                'ansible_ssh_pass': server.password,
                'ansible_become': 'yes',
                'ansible_become_user': 'root',
                'ansible_become_pass': server.password,
                'ansible_python_interpreter': 'python3'
            })
            if server.private_key:
                host['ansible_ssh_private_key_file'] = self.temp.save(
                    server.private_key,
                    directory = 'keys'
                )
            self.hosts.append(host)

    def group_servers(self):
        self.groups = {}

        for server in self.servers:
            for group in server.groups.all():
                if group.name not in self.groups:
                    self.groups[group.name] = {
                        'children': [],
                        'servers': []
                    }
                self.groups[group.name]['servers'].append(self.get_server_id(server))

                while group.parent:
                    if group.parent.name not in self.groups:
                        self.groups[group.parent.name] = {
                            'children': [],
                            'servers': []
                        }
                    if group.name not in self.groups[group.parent.name]['children']:
                        self.groups[group.parent.name]['children'].append(group.name)

                    group = group.parent

    def render(self):
        data = [ '[all]' ]
        for host in self.hosts:
            record = [ self.get_server_id(host.get('server')) ]

            for key, value in host.items():
                if key != 'server':
                    record.append("{}={}".format(key, value))

            data.append(" ".join(record))
        data.append('')

        for name, info in self.groups.items():
            if len(info['children']):
                data.append("[{}:children]".format(name))
                for child in info['children']:
                    data.append(child)
                data.append('')

            if len(info['servers']):
                data.append("[{}]".format(name))
                for server in info['servers']:
                    data.append(server)
                data.append('')

        return "\n".join(data)


class Provider(BaseProvider('task', 'ansible')):

    thread_lock = threading.Semaphore(settings.ANSIBLE_MAX_PROCESSES)


    def execute(self, results, params):
        with temp_dir() as temp:
            env = self._env_vars(params)
            directory = self.field_directory
            project_dir = self.get_module_path() if not directory else self.get_path(directory)

            ansible_config = self.merge_config(directory,
                '[defaults]',
                'host_key_checking = False',
                'deprecation_warnings = False',
                'gathering = smart',
                'force_valid_group_names = ignore',
                'display_skipped_hosts = no'
            )
            inventory = AnsibleInventory(self, self._ssh_servers(params), temp)

            if directory:
                for filename in os.listdir(project_dir):
                    if not filename.endswith(".cfg"):
                        temp.link(os.path.join(project_dir, filename),
                            name = filename
                        )

            ansible_cmd = [
                'ansible-playbook',
                '-i', temp.save(inventory.render())
            ]
            if Runtime.debug():
                ansible_cmd.append('-vvvv')

            playbooks = ensure_list(self.field_playbooks)
            command = ansible_cmd + playbooks

            if self.field_lock:
                params = {}
            else:
                params.pop('servers', None)
                params.pop('filter', None)

            for key, value in self.field_variables.items():
                if key not in params:
                    params[key] = value

            if params:
                command.extend([
                    "--extra-vars",
                    "@{}".format(temp.save(json.dumps(params), extension = 'json'))
                ])

            env["ANSIBLE_CONFIG"] = temp.save(ansible_config, extension = 'cfg')
            with self.thread_lock:
                success = self.command.sh(
                    command,
                    env = env,
                    cwd = project_dir,
                    display = True,
                    line_prefix = '[ansible]: '
                )
            if not success:
                self.command.error("Ansible task failed: {}".format(" ".join(command)))

            self.command.success("Ansible playbooks {} completed successfully".format(", ".join(playbooks)))


    def merge_config(self, ansible_dir, *core_config):
        if not ansible_dir:
            return "\n".join(core_config)
        else:
            ansible_config_file = "{}/{}".format(ansible_dir, 'ansible.cfg')

        config_contents = self.module.load_file(ansible_config_file)

        if not config_contents:
            return "\n".join(core_config)

        config = []
        sections = {}
        curr_section = '[defaults]'

        for line in config_contents.split("\n") + list(core_config):
            line = line.strip()

            if line:
                match = re.search(r'^\[\s*([^\]]+)\s*\]$', line)
                if match:
                    curr_section = match.group(1)

                    if curr_section not in sections:
                        sections[curr_section] = []
                else:
                    if line[0] != '#':
                        sections[curr_section].append(line)

        for section, lines in sections.items():
            config.append("[{}]".format(section))
            config.extend(lines)
            config.append('')

        return "\n".join(config)
