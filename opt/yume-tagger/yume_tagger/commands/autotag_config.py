import configargparse
from yume_tagger import util
from yume_tagger.autotag_settings import AutoTagSettings
from yume_tagger.autotag_settings import deserialize
from yume_tagger.commands.base import BaseCommand


def _serialize_autotag_settings(autotag_settings_: AutoTagSettings) -> str:
    return autotag_settings_.serialize()


def _deserialize_autotag_settings(text: str) -> AutoTagSettings:
    return deserialize(text)


class AutoTagConfigCommand(BaseCommand):
    def run(self, args: configargparse.Namespace) -> None:
        self._autotag_settings.__dict__.update(
            util.run_editor(
                'settings.txt',
                self._autotag_settings,
                _serialize_autotag_settings,
                _deserialize_autotag_settings).__dict__)

    @staticmethod
    def _create_parser(
            parent_parser: configargparse.ArgumentParser
    ) -> configargparse.ArgumentParser:
        return parent_parser.add_parser(
            'autotag-config', help='tweak settings of autotagger')
