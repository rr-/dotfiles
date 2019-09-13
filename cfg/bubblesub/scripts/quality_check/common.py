import typing as T
from copy import copy

from bubblesub.api import Api
from bubblesub.api.log import LogLevel
from bubblesub.ass_renderer import AssRenderer
from bubblesub.fmt.ass.event import AssEvent, AssEventList
from bubblesub.fmt.ass.meta import AssMeta
from bubblesub.fmt.ass.util import ass_to_plaintext

WIDTH_MULTIPLIERS = {1: 0.7, 2: 0.9}

NON_STUTTER_PREFIXES = {"half", "well"}
NON_STUTTER_SUFFIXES = {"kun", "san", "chan", "smaa", "senpai", "sensei"}
NON_STUTTER_WORDS = {"bye-bye", "part-time", "easy-peasy", "ta-da"}
WORDS_WITH_PERIOD = {"vs.", "Mr.", "Jr.", "U.F.O.", "a.k.a."}


class BaseResult:
    def __init__(
        self, event: T.Union[AssEvent, T.List[AssEvent]], text: str
    ) -> None:
        if isinstance(event, list):
            self.event = event[0]
            self.additional_events = event[1:]
        else:
            self.event = event
            self.additional_events = []
        self.text = text

    @property
    def events(self) -> T.Iterable[AssEvent]:
        yield self.event
        yield from self.additional_events

    def __repr__(self) -> str:
        ids = "+".join([f'#{event.number or "?"}' for event in self.events])
        return f"{ids}: {self.text}"


class DebugInformation(BaseResult):
    log_level = LogLevel.Debug


class Information(BaseResult):
    log_level = LogLevel.Info


class Violation(BaseResult):
    log_level = LogLevel.Warning


def measure_frame_size(
    api: Api, renderer: AssRenderer, event: AssEvent
) -> T.Tuple[int, int]:
    fake_event_list = AssEventList()
    fake_event_list.append(copy(event))

    renderer.set_source(
        style_list=renderer.style_list,
        event_list=fake_event_list,
        meta=renderer.meta,
        video_resolution=renderer.video_resolution,
    )

    layers = [
        layer
        for layer in renderer.render_raw(time=event.start)
        if layer.type == 0
    ]
    if not layers:
        return (0, 0)
    min_x = min(layer.dst_x for layer in layers)
    min_y = min(layer.dst_y for layer in layers)
    max_x = max(layer.dst_x + layer.w for layer in layers)
    max_y = max(layer.dst_y + layer.h for layer in layers)
    return (int((max_x - min_x) * api.video.aspect_ratio), max_y - min_y)


def get_optimal_line_heights(
    api: Api, renderer: AssRenderer
) -> T.Dict[str, float]:
    TEST_LINE_COUNT = 20
    VIDEO_RES_X = 100
    VIDEO_RES_Y = TEST_LINE_COUNT * 300

    fake_meta = AssMeta()
    fake_meta.set("WrapStyle", 2)
    renderer.set_source(
        style_list=api.subs.styles,
        event_list=api.subs.events,
        meta=fake_meta,
        video_resolution=(VIDEO_RES_X, VIDEO_RES_Y),
    )

    ret = {}
    for style in api.subs.styles:
        event = AssEvent(
            start=0,
            end=1000,
            text="\\N".join(["gjMW"] * TEST_LINE_COUNT),
            style=style.name,
        )

        _frame_width, frame_height = measure_frame_size(api, renderer, event)
        line_height = frame_height / TEST_LINE_COUNT
        ret[event.style] = line_height
        api.log.debug(f"average height for {event.style}: {line_height}")
    return ret


def get_height(api: Api) -> int:
    return int(api.subs.meta.get("PlayResY", "0"))


def get_width(api: Api) -> int:
    return int(api.subs.meta.get("PlayResX", "0"))


def get_prev_non_empty_event(event: AssEvent) -> T.Optional[AssEvent]:
    event = event.prev
    while event:
        if ass_to_plaintext(event.text) and not event.is_comment:
            return event
        event = event.prev
    return None


def get_next_non_empty_event(event: AssEvent) -> T.Optional[AssEvent]:
    event = event.next
    while event:
        if ass_to_plaintext(event.text) and not event.is_comment:
            return event
        event = event.next
    return None


def is_event_sign(event: AssEvent) -> bool:
    return event.actor == "(sign)"


def is_event_title(event: AssEvent) -> bool:
    return event.actor == "[title]"


def is_event_karaoke(event: AssEvent) -> bool:
    return event.actor == "[karaoke]"


def is_event_credits(event: AssEvent) -> bool:
    return event.actor == "[credits]"


def is_event_dialog(event: AssEvent) -> bool:
    return not (
        is_event_sign(event)
        or is_event_title(event)
        or is_event_karaoke(event)
        or is_event_credits(event)
    )
