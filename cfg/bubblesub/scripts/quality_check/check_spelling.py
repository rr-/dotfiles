from collections import defaultdict

import enchant
from bubblesub.api import Api
from bubblesub.ass.util import ass_to_plaintext, spell_check_ass_line

SPELL_CHECK_LANGUAGE = "en_US"


def check_spelling(api: Api) -> None:
    if not api.subs.path:
        return

    try:
        dictionary = enchant.DictWithPWL(
            SPELL_CHECK_LANGUAGE, pwl=str(api.subs.path.with_name("dict.txt"))
        )
    except enchant.errors.DictNotFoundError:
        api.log.warn(f'Dictionary "{SPELL_CHECK_LANGUAGE}" not found')
        return

    misspelling_map = defaultdict(set)
    for event in api.subs.events:
        if event.actor == "[karaoke]":
            continue
        text = ass_to_plaintext(event.text)
        for _start, _end, word in spell_check_ass_line(dictionary, text):
            misspelling_map[word].add(event.number)

    api.log.info("Misspelt words:")
    for word, line_numbers in sorted(
        misspelling_map.items(), key=lambda item: len(item[1]), reverse=True
    ):
        api.log.warn(
            f"- {word}: " + ", ".join(f"#{num}" for num in line_numbers)
        )
