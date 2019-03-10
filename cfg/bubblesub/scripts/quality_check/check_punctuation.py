import re
import typing as T

from bubblesub.ass.event import AssEvent
from bubblesub.ass.util import ass_to_plaintext

from .common import BaseResult, Violation

NON_STUTTER_PREFIXES = {"half", "well"}
NON_STUTTER_SUFFIXES = {"kun", "san", "chan", "smaa", "senpai", "sensei"}
NON_STUTTER_WORDS = {"bye-bye", "part-time", "easy-peasy"}


def check_punctuation(event: AssEvent) -> T.Iterable[BaseResult]:
    text = ass_to_plaintext(event.text)

    if text.startswith("\n") or text.endswith("\n"):
        yield Violation(event, "extra line break")
    elif re.search(r"^\s|\s$", text):
        yield Violation(event, "extra whitespace")

    if text.count("\n") >= 2:
        yield Violation(event, "three or more lines")

    if re.search(r"\n\s|\s\n", text):
        yield Violation(event, "whitespace around line break")

    if re.search(r"\n[.,?!:;]", text):
        yield Violation(event, "line break before punctuation")
    elif re.search(r"\s[.,?!:;]", text):
        yield Violation(event, "whitespace before punctuation")

    if "  " in text:
        yield Violation(event, "double space")

    if "..." in text:
        yield Violation(event, "bad ellipsis (expected …)")
    elif re.search("[…,.!?:;][,.]", text):
        yield Violation(event, "extra comma or dot")

    context = re.split(r"\W+", re.sub('[.,?!"]', "", text.lower()))
    for word in {
        "im",
        "youre",
        "hes",
        "shes",
        "theyre",
        "isnt",
        "arent",
        "wasnt",
        "werent",
        "didnt",
        "thats",
        "heres",
        "theres",
        "wheres",
        "cant",
        "dont",
        "wouldnt",
        "couldnt",
        "shouldnt",
        "hasnt",
        "havent",
        "ive",
        "wouldve",
        "youve",
        "ive",
    }:
        if word in context:
            yield Violation(event, "missing apostrophe")

    if re.search("^– .* –$", text, flags=re.M):
        yield Violation(event, "bad dash (expected —)")
    elif not re.search("^—.*—$", text, flags=re.M):
        if len(re.findall(r"^–", text, flags=re.M)) == 1:
            yield Violation(event, "dialog with just one person")

        if re.search(r"[-–]$", text, flags=re.M):
            yield Violation(event, "bad dash (expected —)")

        if re.search(r"^- |^—", text, flags=re.M):
            yield Violation(event, "bad dash (expected –)")

        if re.search(r" - ", text, flags=re.M):
            yield Violation(event, "bad dash (expected –)")

    if re.search(r" —|— ", text):
        yield Violation(event, "whitespace around —")

    match = re.search(r"(\w+[\.!?])\s+[a-z]", text, flags=re.M)
    if match:
        if match.group(1) not in {"vs."}:
            yield Violation(event, "lowercase letter after sentence end")

    match = re.search(r"^([A-Z][a-z]{,3})-([a-z]+)", text, flags=re.M)
    if match:
        if (
            match.group(0).lower() not in NON_STUTTER_WORDS
            and match.group(1).lower() not in NON_STUTTER_PREFIXES
            and match.group(2).lower() not in NON_STUTTER_SUFFIXES
        ):
            yield Violation(event, "possibly wrong stutter capitalization")

    if re.search(r"[\.,?!:;][A-Za-z]|[a-zA-Z]…[A-Za-z]", text):
        yield Violation(event, "missing whitespace after punctuation mark")

    if re.search(
        "\\s|\N{ZERO WIDTH SPACE}", text.replace(" ", "").replace("\n", "")
    ):
        yield Violation(event, "unrecognized whitespace")
