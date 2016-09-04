import coloredlogs
from logging import *


def _add_custom_level(number, name):
    addLevelName(number, name.upper())

    def handler(self, message, *args, **kws):
        if self.isEnabledFor(number):
            self._log(number, message, args, **kws)

    setattr(Logger, name, handler)


_add_custom_level(29, 'success')

coloredlogs.install(fmt='%(message)s', level_styles={
    'warning': {'color': 'yellow'},
    'success': {'color': 'green', 'bold': True},
    'error': {'color': 'red', 'bold': True},
    'info': {'color': 'blue', 'bold': True},
})
