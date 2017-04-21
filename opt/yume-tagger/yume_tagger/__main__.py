#!/usr/bin/env python3
import sys
import getpass
from typing import Optional
import configargparse
from filelock import FileLock
from yume_tagger.api import Api, ApiError
from yume_tagger import autotag_settings
from yume_tagger import util
from yume_tagger.commands import AutoTagNewestPostCommand
from yume_tagger.commands import AutoTagChosenPostCommand
from yume_tagger.commands import AutoTagConfigCommand
from yume_tagger.commands import AutoTagError
from yume_tagger.commands import EditTagsCommand


AUTOTAGGER_SETTINGS_PATH = util.DB_DIR.joinpath('settings.txt')


def parse_args() -> Optional[configargparse.Namespace]:
    parser = configargparse.ArgumentParser(
        description='Yume.pl tag manager',
        default_config_files=['~/.config/yume-tagger.conf'])
    parser.add_argument(
        '-c', '--config', metavar='PATH', is_config_file=True,
        help='config file path')
    parser.add_argument('-u', '--user')
    parser.add_argument('-p', '--password')
    subparsers = parser.add_subparsers(
        help='choose the command', dest='command')
    EditTagsCommand.decorate_parser(subparsers)
    AutoTagNewestPostCommand.decorate_parser(subparsers)
    AutoTagChosenPostCommand.decorate_parser(subparsers)
    AutoTagConfigCommand.decorate_parser(subparsers)
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return None
    return args


def main() -> None:
    args = parse_args()
    if not args:
        sys.exit(1)

    user_name: str = args.user or input('User: ')
    password: str = args.password or getpass.getpass('Password: ')

    with FileLock(str(AUTOTAGGER_SETTINGS_PATH) + '.lock'):
        autotag_settings_ = autotag_settings.load(AUTOTAGGER_SETTINGS_PATH)

        try:
            api = Api()
            api.login(user_name, password)
            args.command(api, autotag_settings_).run(args)
            sys.exit(0)
        except (ApiError, AutoTagError) as ex:
            print(ex, file=sys.stderr)
            sys.exit(1)
        finally:
            autotag_settings_.save(AUTOTAGGER_SETTINGS_PATH)


if __name__ == '__main__':
    main()
