# pylint: disable=unused-import,protected-access,invalid-name
import logging
import os
from collections.abc import Callable
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
from typing import Any

try:
    import coloredlogs
except ImportError:
    coloredlogs = None


def _add_custom_level(
    number: int, name: str
) -> tuple[int, Callable[..., None]]:
    logging.addLevelName(number, name.upper())

    def member(self: Any, message: str, *args: Any, **kwargs: Any) -> None:
        if self.isEnabledFor(number):
            self._log(number, message, args, **kwargs)

    def function(message: str, *args: Any, **kwargs: Any) -> None:
        if len(logging.Logger.root.handlers) == 0:
            logging.basicConfig()
        logging.Logger.root._log(number, message, args, **kwargs)

    setattr(logging.Logger, name, member)
    return (number, function)


SUCCESS, success = _add_custom_level(29, "success")


def setup_colored_logs(fmt: str = "%(message)s") -> None:
    if coloredlogs is None:
        return
    coloredlogs.install(
        fmt=fmt,
        level_styles={
            "warning": {"color": "yellow"},
            "success": {"color": "green", "bold": True},
            "error": {"color": "red", "bold": True},
            "info": {},
        },
        isatty=True if "COLORED_LOGS" in os.environ else None,
    )
