#!/usr/bin/env python
# Copyright (c) 2013 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
from cliff.app import App
from cliff.commandmanager import CommandManager
from cliff.help import HelpAction
import shaddock.frontend
from shaddock.openstack.common import cliutils as c
import logging
import sys


class ShaddockShell(App):

    log = logging.getLogger(__name__)

    def __init__(self):
        super(ShaddockShell, self).__init__(
            description='Shaddock shell',
            version='0.3.2',
            command_manager=CommandManager('shaddock.cli'))
        self._set_shell_commands(self._get_commands())

    def configure_logging(self):
        super(ShaddockShell, self).configure_logging()
        logging.getLogger('iso8601').setLevel(logging.WARNING)
        if self.options.verbose_level <= 1:
            logging.getLogger('requests').setLevel(logging.WARNING)

    def build_option_parser(self, description, version,
                            argparse_kwargs=None):
        """Return an argparse option parser for this application.

        Subclasses may override this method to extend
        the parser with more global options.

        :param description: full description of the application
        :paramtype description: str
        :param version: version number for the application
        :paramtype version: str
        :param argparse_kwargs: extra keyword argument passed to the
                                ArgumentParser constructor
        :paramtype extra_kwargs: dict
        """
        argparse_kwargs = argparse_kwargs or {}
        parser = argparse.ArgumentParser(
            description=description,
            add_help=False,
            **argparse_kwargs
        )
        parser.add_argument(
            '--version',
            action='version',
            version='%(prog)s {0}'.format(version),
            help='Show program\'s version number and exit.'
        )
        parser.add_argument(
            '-v', '--verbose',
            action='count',
            dest='verbose_level',
            default=self.DEFAULT_VERBOSE_LEVEL,
            help='Increase verbosity of output. Can be repeated.',
        )
        parser.add_argument(
            '--log-file',
            action='store',
            default=None,
            help='Specify a file to log output. Disabled by default.',
        )
        parser.add_argument(
            '-q', '--quiet',
            action='store_const',
            dest='verbose_level',
            const=0,
            help='Suppress output except warnings and errors.',
        )
        parser.add_argument(
            '-h', '--help',
            action=HelpAction,
            nargs=0,
            default=self,  # tricky
            help="Show this help message and exit.",
        )
        parser.add_argument(
            '--debug',
            default=False,
            action='store_true',
            help='Show tracebacks on errors.',
        )
        parser.add_argument(
            '--docker-host',
            action='store',
            dest='docker_host',
            default=c.env('DOCKER_HOST',
                          default='unix://var/run/docker.sock'),
            help='IP/hostname to the Docker API.  (Env: DOCKER_HOST)'
        )
        parser.add_argument(
            '--docker-version',
            action='store',
            dest='docker_version',
            default=c.env('DOCKER_VERSION',
                          default='1.12'),
            help='Docker API version number (Env: DOCKER_VERSION)'
        )

        parser.add_argument(
            '--template-dir',
            action='store',
            dest='template_dir',
            default=c.env('SHDK_TEMPLATEDIR',
                          default='/var/lib/shaddock'),
            help='Template directory to use. (Env: SHDK_TEMPLATE_DIR)'
        )
        return parser

    def initialize_app(self, argv):
        self._clear_shell_commands()
        self._set_shell_commands(self._get_commands())

    def _set_shell_commands(self, cmds_dict):
        for k, v in cmds_dict.items():
            self.command_manager.add_command(k, v)

    @staticmethod
    def _get_commands():
        return {
            'build': shaddock.frontend.Build,
            'create': shaddock.frontend.Create,
            'start': shaddock.frontend.Start,
            'logs': shaddock.frontend.Logs,
            'stop': shaddock.frontend.Stop,
            'restart': shaddock.frontend.Restart,
            'remove': shaddock.frontend.Remove,
            'list': shaddock.frontend.List,
            'show': shaddock.frontend.Show
        }

    def _clear_shell_commands(self):
        exclude_cmds = ['help', 'complete']

        cmds = self.command_manager.commands.copy()
        for k, v in cmds.items():
            if k not in exclude_cmds:
                self.command_manager.commands.pop(k)

    def prepare_to_run_command(self, cmd):
        self.log.debug('prepare_to_run_command %s', cmd.__class__.__name__)

    def clean_up(self, cmd, result, err):
        self.log.debug('clean_up %s', cmd.__class__.__name__)
        if err:
            self.log.debug('got an error: %s', err)


def main(argv=sys.argv[1:]):
    return ShaddockShell().run(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))