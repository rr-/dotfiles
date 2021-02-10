# pylint: disable=unused-import,protected-access,invalid-name
import logging
import os
from logging import (
    DEBUG,
    ERROR,
    INFO,
    WARNING,
    debug,
    error,
    getLogger,
    info,
    warning,
)

import coloredlogs


def _add_custom_level(number, name):
    logging.addLevelName(number, name.upper())

    def member(self, message, *args, **kwargs):
        if self.isEnabledFor(number):
            self._log(number, message, args, **kwargs)

    def function(message, *args, **kwargs):
        if len(logging.Logger.root.handlers) == 0:
            logging.basicConfig()
        logging.Logger.root._log(number, message, args, **kwargs)

    setattr(logging.Logger, name, member)
    return (number, function)


SUCCESS, success = _add_custom_level(29, "success")


def setup_colored_logs(fmt: str = "%(message)s") -> None:
    coloredlogs.install(
        fmt=fmt,
        level_styles={
            "warning": {"color": "yellow"},
            "success": {"color": "green", "bold": True},
            "error": {"color": "red", "bold": True},
            "info": {"color": "blue", "bold": True},
        },
        isatty=True if "COLORED_LOGS" in os.environ else None,
    )
