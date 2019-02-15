import functools

import ass_tag_parser
from bubblesub.api.cmd import BaseCommand
from bubblesub.cfg.menu import MenuCommand


def ms_to_str(ms: int) -> str:
    return str(ms // 1000)


def extract_text(text: str) -> str:
    try:
        ass_line = ass_tag_parser.parse_ass(text)
    except ass_tag_parser.ParseError as ex:
        return text
    ret = ""
    for item in ass_line:
        if isinstance(item, ass_tag_parser.AssText):
            ret += item.text
    return functools.reduce(
        lambda ret, word: ret.replace(word, ""), list("…♪"), ret
    ).strip()


class ProgressCommand(BaseCommand):
    names = ["progress"]
    help_text = "How much left"

    async def run(self):
        empty_count = 0
        empty_duration = 0
        total_count = 0
        total_duration = 0
        for event in self.api.subs.events:
            if event.actor.startswith("[") and event.actor.endswith("]"):
                continue
            total_duration += event.duration
            total_count += 1
            if not extract_text(event.text):
                empty_duration += event.duration
                empty_count += 1

        self.api.log.info(
            f"{empty_count} lines left ("
            f"{total_count-empty_count}/{total_count}, "
            f"{(total_count-empty_count)/total_count:.01%})"
        )
        self.api.log.info(
            f"{ms_to_str(empty_duration)} seconds left ("
            f"{ms_to_str(total_duration-empty_duration)}/"
            f"{ms_to_str(total_duration)}, "
            f"{(total_duration-empty_duration)/total_duration:.01%})"
        )


COMMANDS = [ProgressCommand]
MENU = [MenuCommand("Show translation &progress", "progress")]
