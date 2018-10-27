import configargparse
from yume_tagger.api import Api
from yume_tagger.autotag_settings import AutoTagSettings


class BaseCommand:
    def __init__(self, api: Api, autotag_settings: AutoTagSettings) -> None:
        self._api = api
        self._autotag_settings = autotag_settings

    @classmethod
    def decorate_parser(
        cls, parent_parser: configargparse.ArgumentParser
    ) -> None:
        parser = cls._create_parser(parent_parser)
        parser.set_defaults(command=cls)

    def run(self, args: configargparse.Namespace) -> None:
        raise NotImplementedError("Not implemented")

    @staticmethod
    def _create_parser(
        parent_parser: configargparse.ArgumentParser
    ) -> configargparse.ArgumentParser:
        raise NotImplementedError("Not implemented")
