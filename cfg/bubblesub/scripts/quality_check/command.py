import argparse
import bisect
import re
import typing as T

from bubblesub.api import Api
from bubblesub.api.cmd import BaseCommand
from bubblesub.api.log import LogLevel
from bubblesub.ass_renderer import AssRenderer

from .check_actors import check_actors
from .check_ass_tags import check_ass_tags
from .check_double_words import check_double_words
from .check_durations import check_durations
from .check_fonts import check_fonts
from .check_line_continuation import check_line_continuation
from .check_long_line import check_long_line
from .check_punctuation import check_punctuation
from .check_quotes import check_quotes
from .check_spelling import check_spelling
from .check_style_validity import check_style_validity
from .check_styles import check_styles
from .check_unnecessary_breaks import check_unnecessary_breaks
from .common import BaseResult, get_height, get_optimal_line_heights, get_width


def list_violations(api: Api) -> T.Iterable[BaseResult]:
    renderer = AssRenderer()
    optimal_line_heights = get_optimal_line_heights(api, renderer)
    renderer.set_source(
        style_list=api.subs.styles,
        event_list=api.subs.events,
        meta=api.subs.meta,
        video_resolution=(get_width(api), get_height(api)),
    )

    for event in api.subs.events:
        yield from check_style_validity(event, api.subs.styles)
        yield from check_durations(event)
        yield from check_punctuation(event)
        yield from check_quotes(event)
        yield from check_line_continuation(event)
        yield from check_ass_tags(event)
        yield from check_double_words(event)
        yield from check_unnecessary_breaks(
            event, api, renderer, optimal_line_heights
        )
        yield from check_long_line(event, api, renderer, optimal_line_heights)


class QualityCheckCommand(BaseCommand):
    names = ["qc", "quality-check"]
    help_text = "Tries to pinpoint common issues with the subtitles."

    @staticmethod
    def decorate_parser(api: Api, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("-p", "--focus-prev", action="store_true")
        parser.add_argument("-n", "--focus-next", action="store_true")

    async def run(self):
        if self.args.focus_prev or self.args.focus_next:
            violations = [
                result
                for result in list_violations(self.api)
                if result.log_level in {LogLevel.Warning, LogLevel.Error}
            ]
            violated_indexes = sorted(
                violation.event.index for violation in violations
            )

            if self.args.focus_prev:
                selected_index = self.api.subs.selected_indexes[0]
                next_index = violated_indexes[
                    bisect.bisect_left(violated_indexes, selected_index) - 1
                ]

            elif self.args.focus_next:
                selected_index = self.api.subs.selected_indexes[-1]
                next_index = violated_indexes[
                    bisect.bisect_right(violated_indexes, selected_index)
                    % len(violated_indexes)
                ]

            else:
                raise AssertionError

            self.api.subs.selected_indexes = [next_index]
            for result in violations:
                if result.event.index == next_index:
                    self.api.log.log(result.log_level, repr(result))
            return

        results = sorted(
            list_violations(self.api),
            key=lambda result: (
                re.match("^([^(]*).*?$", result.text).group(1),
                result.event.number,
            ),
        )
        for result in results:
            self.api.log.log(result.log_level, repr(result))

        check_spelling(self.api)
        check_actors(self.api)
        check_styles(self.api)
        check_fonts(self.api)
