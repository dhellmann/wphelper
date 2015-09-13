import sys

from cliff.app import App
from cliff.commandmanager import CommandManager

import pkg_resources


class WPHelper(App):

    def __init__(self):
        version = pkg_resources.get_distribution('wphelper').version
        super(WPHelper, self).__init__(
            description='WordPress helper',
            version=version,
            command_manager=CommandManager('wphelper.commands'),
            deferred_help=True,
        )


def main(argv=sys.argv[1:]):
    myapp = WPHelper()
    return myapp.run(argv)
