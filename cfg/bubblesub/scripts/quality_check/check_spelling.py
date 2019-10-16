import typing as T
from collections import defaultdict

from bubblesub.api import Api
from bubblesub.fmt.ass.util import ass_to_plaintext, spell_check_ass_line
from bubblesub.spell_check import SpellChecker, SpellCheckerError

from .common import is_event_karaoke

SPELL_CHECK_LANGUAGE = "en_US"


def check_spelling(spell_check_lang: T.Optional[str], api: Api) -> None:
    if not api.subs.path:
        return

    if not spell_check_lang:
        api.log.warn("Spell check was disabled in config.")
        return

    try:
        dictionary = SpellChecker(spell_check_lang)
    except SpellCheckerError as ex:
        api.log.error(str(ex))
        return

    exceptions_case_sensitive: T.List[str] = []
    exceptions_case_insensitive: T.List[str] = []
    dict_names = [f"dict-{spell_check_lang}.txt", "dict.txt"]
    for dict_name in dict_names:
        dict_path = api.subs.path.with_name(dict_name)
        if dict_path.exists():
            for line in dict_path.read_text().splitlines():
                if line.islower():
                    exceptions_case_insensitive.append(line.lower())
                else:
                    exceptions_case_sensitive.append(line)
            break

    misspelling_map = defaultdict(set)
    for event in api.subs.events:
        if is_event_karaoke(event):
            continue
        text = ass_to_plaintext(event.text)
        for _start, _end, word in spell_check_ass_line(dictionary, text):
            if (
                word not in exceptions_case_sensitive
                and word.lower() not in exceptions_case_insensitive
            ):
                misspelling_map[word].add(event.number)

    if misspelling_map:
        api.log.info("Misspelled words:")
        for word, line_numbers in sorted(
            misspelling_map.items(),
            key=lambda item: len(item[1]),
            reverse=True,
        ):
            api.log.warn(
                f"- {word}: " + ", ".join(f"#{num}" for num in line_numbers)
            )
    else:
        api.log.info("No misspelled words")
