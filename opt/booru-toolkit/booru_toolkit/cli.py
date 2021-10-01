from getpass import getpass
from typing import Any, cast

import configargparse

from booru_toolkit.plugin.base import PluginBase


def make_arg_parser(
    description: str, plugins: list[PluginBase]
) -> configargparse.Parser:
    class CustomHelpFormatter(configargparse.HelpFormatter):
        def _format_action_invocation(
            self, action: configargparse.Action
        ) -> str:
            if not action.option_strings or action.nargs == 0:
                return cast(str, super()._format_action_invocation(action))
            default = self._get_default_metavar_for_optional(action)
            args_string = cast(str, self._format_args(action, default))
            return ", ".join(action.option_strings) + " " + args_string

    class PluginAction(configargparse.Action):
        def __call__(
            self,
            parser: configargparse.Parser,
            args: configargparse.Namespace,
            values: Any,
            option_string: Any = None,
        ) -> None:
            assert isinstance(values, str)
            plugin = next(
                plugin for plugin in plugins if plugin.name == values
            )
            setattr(args, self.dest, plugin)

    parser = configargparse.ArgumentParser(
        description=description, formatter_class=CustomHelpFormatter
    )
    parser.add(
        "-c",
        "--config",
        metavar="PATH",
        is_config_file=True,
        help="config file path",
    )
    parser.add(
        "--plugin",
        metavar="PLUGIN",
        required=True,
        choices=[plugin.name for plugin in plugins],
        action=PluginAction,
        help="API to use ({{{}}})".format(
            ",".join(plugin.name for plugin in plugins)
        ),
    )
    parser.add(
        "-u",
        "--user",
        help="API user name (leave empty to input interactively)",
    )
    parser.add(
        "-p",
        "--pass",
        dest="password",
        help="API user password (leave empty to input interactively)",
    )

    old_parse_args = parser.parse_args

    def new_parse_args() -> configargparse.Namespace:
        result = old_parse_args()
        while not result.user:
            result.user = input("User: ")
        while not result.password:
            result.password = getpass("Password: ")
        return result

    parser.parse_args = new_parse_args
    return parser
