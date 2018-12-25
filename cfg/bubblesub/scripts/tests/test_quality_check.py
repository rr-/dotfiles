import re
import typing as T

import pytest

from bubblesub.api.log import LogLevel
from bubblesub.ass.event import Event, EventList

from ..quality_check import (
    Violation,
    check_ass_tags,
    check_double_words,
    check_durations,
    check_line_continuation,
    check_punctuation,
    check_quotes,
)


def test_violation_single_event() -> None:
    event_list = EventList()
    event_list.append(Event(start=0, end=0))
    violation = Violation(event_list[0], "test")
    assert repr(violation) == "#1: test"


def test_violation_multiple_events() -> None:
    event_list = EventList()
    event_list.append(Event(start=0, end=0))
    event_list.append(Event(start=0, end=0))
    violation = Violation([event_list[0], event_list[1]], "test")
    assert repr(violation) == "#1+#2: test"


def test_check_durations_empty_text() -> None:
    event = Event(start=0, end=100)
    assert len(list(check_durations(event))) == 0


def test_check_durations_comment() -> None:
    event = Event(start=0, end=100, text="test", is_comment=True)
    assert len(list(check_durations(event))) == 0


def test_check_durations_too_short() -> None:
    event = Event(start=0, end=100, text="test")
    results = list(check_durations(event))
    assert len(results) == 1
    assert results[0].text == "duration shorter than 250 ms"


def test_check_durations_too_short_long_text() -> None:
    event = Event(start=0, end=100, text="test test test test test")
    results = list(check_durations(event))
    assert len(results) == 1
    assert results[0].text == "duration shorter than 500 ms"


def test_check_durations_good_duration() -> None:
    event = Event(start=0, end=501, text="test test test test test")
    assert len(list(check_durations(event))) == 0


def test_check_durations_too_short_gap() -> None:
    event_list = EventList()
    event_list.append(Event(start=0, end=500, text="test"))
    event_list.append(Event(start=600, end=900, text="test"))
    results = list(check_durations(event_list[0]))
    assert len(results) == 1
    assert results[0].text == "gap shorter than 250 ms (100 ms)"


def test_check_durations_too_short_gap_empty_lines() -> None:
    event_list = EventList()
    event_list.append(Event(start=0, end=500, text="test"))
    event_list.append(Event(start=550, end=550))
    event_list.append(Event(start=600, end=900, text="test"))
    results = list(check_durations(event_list[0]))
    assert len(results) == 1
    assert results[0].text == "gap shorter than 250 ms (100 ms)"


def test_check_durations_too_short_gap_comments() -> None:
    event_list = EventList()
    event_list.append(Event(start=0, end=500, text="test"))
    event_list.append(Event(start=550, end=550, text="test", is_comment=True))
    event_list.append(Event(start=600, end=900, text="test"))
    results = list(check_durations(event_list[0]))
    assert len(results) == 1
    assert results[0].text == "gap shorter than 250 ms (100 ms)"


def test_check_durations_good_gap() -> None:
    event_list = EventList()
    event_list.append(Event(start=0, end=500, text="test"))
    event_list.append(Event(start=750, end=900, text="test"))
    assert len(list(check_durations(event_list[0]))) == 0


@pytest.mark.parametrize(
    "text, violation_text",
    [
        ("Text\\N", "extra line break"),
        ("\\NText", "extra line break"),
        ("Text\\NText\\NText", "three or more lines"),
        ("Text\\N Text", "whitespace around line break"),
        ("Text \\NText", "whitespace around line break"),
        ("Text ", "extra whitespace"),
        (" Text", "extra whitespace"),
        ("Text  text", "double space"),
        ("...", "bad ellipsis (expected …)"),
        ("What youve done", "missing apostrophe"),
        ("- What?\\N- No!", "bad dash (expected \N{EN DASH})"),
        (
            "\N{EM DASH}What?\\N\N{EM DASH}No!",
            "bad dash (expected \N{EN DASH})",
        ),
        ("\N{EM DASH}What?", "bad dash (expected \N{EN DASH})"),
        ("\N{EN DASH} Title \N{EN DASH}", "bad dash (expected \N{EM DASH})"),
        ("\N{EM DASH}Title\N{EM DASH}", None),
        ("\N{EM DASH}Whatever\N{EM DASH}…", "bad dash (expected \N{EN DASH})"),
        ("- What?", "bad dash (expected \N{EN DASH})"),
        ("\N{EN DASH} What!", "dialog with just one person"),
        ("What--", "bad dash (expected \N{EM DASH})"),
        ("What\N{EN DASH}", "bad dash (expected \N{EM DASH})"),
        ("W-what?", "possibly wrong stutter capitalization"),
        ("Ayuhara-san", None),
        ("What! what…", "lowercase letter after sentence end"),
        ("What. what…", "lowercase letter after sentence end"),
        ("Japan vs. the world", None),
        ("Japan vss. the world", "lowercase letter after sentence end"),
        ("What? what…", "lowercase letter after sentence end"),
        ("What , no.", "whitespace before punctuation"),
        ("What !", "whitespace before punctuation"),
        ("What .", "whitespace before punctuation"),
        ("What ?", "whitespace before punctuation"),
        ("What :", "whitespace before punctuation"),
        ("What ;", "whitespace before punctuation"),
        ("What\\N, no.", "line break before punctuation"),
        ("What\\N!", "line break before punctuation"),
        ("What\\N.", "line break before punctuation"),
        ("What\\N?", "line break before punctuation"),
        ("What\\N:", "line break before punctuation"),
        ("What\\N;", "line break before punctuation"),
        ("What?No!", "missing whitespace after punctuation mark"),
        ("What!No!", "missing whitespace after punctuation mark"),
        ("What.No!", "missing whitespace after punctuation mark"),
        ("What,no!", "missing whitespace after punctuation mark"),
        ("What:no!", "missing whitespace after punctuation mark"),
        ("What;no!", "missing whitespace after punctuation mark"),
        ("What…no!", "missing whitespace after punctuation mark"),
        ("What? No!", None),
        ("What! No!", None),
        ("What. No!", None),
        ("What, no!", None),
        ("What: no!", None),
        ("What; no!", None),
        ("What… no!", None),
        ("What?\\NNo!", None),
        ("What!\\NNo!", None),
        ("What.\\NNo!", None),
        ("What,\\Nno!", None),
        ("What:\\Nno!", None),
        ("What;\\Nno!", None),
        ("What…\\Nno!", None),
        ("test\ttest", "unrecognized whitespace"),
        ("test\N{ZERO WIDTH SPACE}test", "unrecognized whitespace"),
        ("….", "extra comma or dot"),
        (",.", "extra comma or dot"),
        ("?.", "extra comma or dot"),
        ("!.", "extra comma or dot"),
        (":.", "extra comma or dot"),
        (";.", "extra comma or dot"),
        ("…,", "extra comma or dot"),
        (",,", "extra comma or dot"),
        ("?,", "extra comma or dot"),
        ("!,", "extra comma or dot"),
        (":,", "extra comma or dot"),
        (";,", "extra comma or dot"),
    ],
)
def test_check_punctuation(text: str, violation_text: T.Optional[str]) -> None:
    event = Event(text=text)
    results = list(check_punctuation(event))
    if violation_text is None:
        assert len(results) == 0
    else:
        assert len(results) == 1
        assert results[0].text == violation_text


@pytest.mark.parametrize(
    "text, violation_text_re, log_level",
    [
        ('"What…', "partial quote", LogLevel.Info),
        ('…what."', "partial quote", LogLevel.Info),
        ('"What."', ".*inside.*marks", LogLevel.Debug),
        ('"What".', ".*outside.*", LogLevel.Debug),
        ('"What", he said.', ".*outside.*", LogLevel.Debug),
        ('"What." he said.', ".*inside.*", LogLevel.Debug),
        ('"What!" he said.', ".*inside.*", LogLevel.Debug),
        ('"What?" he said.', ".*inside.*", LogLevel.Debug),
        ('"What…" he said.', ".*inside.*", LogLevel.Debug),
        ('"What," he said.', ".*inside.*", LogLevel.Warning),
        ('He said "what."', ".*inside.*", LogLevel.Warning),
        ('He said "what!"', ".*inside.*", LogLevel.Warning),
        ('He said "what?"', ".*inside.*", LogLevel.Warning),
        ('He said "what…"', ".*inside.*", LogLevel.Warning),
    ],
)
def test_check_quotes(
    text: str, violation_text_re: str, log_level: LogLevel
) -> None:
    event_list = EventList()
    event_list.append(Event(text=text))
    results = list(check_quotes(event_list[0]))
    assert len(results) == 1
    assert re.match(violation_text_re, results[0].text)
    assert results[0].log_level == log_level


@pytest.mark.parametrize(
    "texts, violation_text",
    [
        (["Whatever…"], None),
        (["Whatever…", "I don't care."], None),
        (["…okay."], None),
        (["Whatever…", "…you say."], "old-style line continuation"),
        (["Whatever", "you say."], None),
        (["Whatever,", "we don't care."], None),
        (["Whatever:", "we don't care."], None),
        (["whatever."], "sentence begins with a lowercase letter"),
        (
            ["Whatever.", "whatever."],
            "sentence begins with a lowercase letter",
        ),
        (["Whatever"], "possibly unended sentence"),
        (["Whatever", "Whatever."], "possibly unended sentence"),
        (["Japan vs.", "the rest."], None),
        (
            ["Japan vss.", "the rest."],
            "sentence begins with a lowercase letter",
        ),
    ],
)
def test_check_line_continuation(
    texts: T.List[str], violation_text: T.Optional[str]
) -> None:
    event_list = EventList()
    for i, text in enumerate(texts):
        event_list.append(Event(text=text))

    results = []
    for event in event_list:
        results += list(check_line_continuation(event))

    if violation_text is None:
        assert len(results) == 0
    else:
        assert len(results) == 1
        assert results[0].text == violation_text


@pytest.mark.parametrize(
    "text, violation_text_re",
    [
        ("text", None),
        ("{\\an8}", None),
        ("text{\\b1}text", None),
        ("{\\fsherp}", "invalid syntax (.*)"),
        ("{}", "pointless ASS tag"),
        ("{\\\\comment}", "use notes to make comments"),
        ("{\\comment}", "invalid syntax (.*)"),
        ("{\\a5}", "using legacy alignment tag"),
        ("{\\an8comment}", "use notes to make comments"),
        ("{comment\\an8}", "use notes to make comments"),
        ("{\\an8}{\\fs5}", "disjointed tags"),
    ],
)
def test_check_ass_tags(text, violation_text_re):
    event_list = EventList()
    event_list.append(Event(text=text))
    results = list(check_ass_tags(event_list[0]))
    if violation_text_re is None:
        assert len(results) == 0
    else:
        assert len(results) == 1
        assert re.match(violation_text_re, results[0].text)


@pytest.mark.parametrize(
    "text, violation_text",
    [
        ("text", None),
        ("text text", "double word (text)"),
        ("text{} text", "double word (text)"),
        ("text{}\\Ntext", "double word (text)"),
        ("text{}text", None),
    ],
)
def test_check_double_words(text, violation_text):
    event_list = EventList()
    event_list.append(Event(text=text))
    results = list(check_double_words(event_list[0]))
    if violation_text is None:
        assert len(results) == 0
    else:
        assert len(results) == 1
        assert results[0].text == violation_text
