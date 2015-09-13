import abc
import configparser
import logging
import os

from cliff.command import Command
from wordpress_xmlrpc import Client
from wordpress_xmlrpc import exceptions as wp_exceptions


class WithCredentials(Command):
    "base class for commands that use WP credentials"

    LOG = logging.getLogger(__name__)

    DEFAULT_CONFIG_FILE = os.path.expanduser('~/.wphelper')

    def get_parser(self, prog_name):
        parser = super(WithCredentials, self).get_parser(prog_name)
        parser.add_argument(
            '-c', '--config-file',
            dest='config_file',
            default=self.DEFAULT_CONFIG_FILE,
            help='configuration file, defaults to %(default)s',
        )
        parser.add_argument(
            '-n', '--dry-run',
            dest='dry_run',
            default=False,
            action='store_true',
            help='report on the actions to take, but do not take them',
        )
        return parser

    def _load_config_file(self, parsed_args):
        "Load our configuration file"
        self.config = configparser.ConfigParser()
        files_found = self.config.read(parsed_args.config_file)
        if not files_found:
            raise RuntimeError('Did not find configuration file %s' %
                               parsed_args.config_file)
        try:
            self.site_url = self.config['site']['url']
            self.xmlrpc_url = self.site_url + '/xmlrpc.php'
        except configparser.Error:
            raise RuntimeError('Missing site/url configuration setting')
        try:
            self.username = self.config['site']['username']
        except configparser.Error:
            raise RuntimeError('Missing site/username configuration setting')
        try:
            self.password = self.config['site']['password']
        except configparser.Error:
            raise RuntimeError('Missing site/password configuration setting')
        self.LOG.info('connecting to %s as %s' %
                      (self.site_url, self.username))

    _WP_FAILURE_MODES = (
        IOError,
        wp_exceptions.InvalidCredentialsError,
        wp_exceptions.ServerConnectionError,
    )

    def _create_connection(self, parsed_args):
        try:
            self.wp = Client(self.xmlrpc_url, self.username, self.password)
        except self._WP_FAILURE_MODES as err:
            self.LOG.error('Could not connect to %s' % self.xmlrpc_url)
            self.LOG.error('Bad site/url or XML-RPC  is not enabled: %s' % err)
            raise

    def take_action(self, parsed_args):
        self._load_config_file(parsed_args)
        self._create_connection(parsed_args)
        return self._take_action(parsed_args)

    @abc.abstractmethod
    def _take_action(self, parsed_args):
        "override this method to provide the real implementation"
