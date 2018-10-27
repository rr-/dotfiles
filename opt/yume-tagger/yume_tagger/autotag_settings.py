import re
import itertools
from pathlib import Path
from typing import Optional, Tuple, Set, List, Dict


SECTION_TAGGED_POST_IDS = "Tagged post IDs"
SECTION_UNTAGGED_POST_IDS = "Untagged post IDs"
SECTION_BANNED_TAG_REGEXES = "Banned tag regexes"
SECTION_BANNED_TAGS = "Banned tags"
SECTION_TAG_MAP = "Tag translations"
SECTION_TAG_CATEGORY_MAP = "Tag category translations"


def _from_int_set(source: Set[int]) -> List[str]:
    ranges: List[Tuple[int, int]] = []
    for _, group_iter in itertools.groupby(
        enumerate(sorted(source)), lambda i: i[1] - i[0]
    ):
        group = list(group_iter)
        ranges.append((group[0][1], group[-1][1]))
    return [
        ",".join(
            (str(low) if low == high else "{}-{}".format(low, high))
            for low, high in ranges
        )
    ]


def _from_str_set(source: Set[str]) -> List[str]:
    return list(sorted(source))


def _from_str_dict(source: Dict[str, str]) -> List[str]:
    return ["{} -> {}".format(left, right) for left, right in source.items()]


def _to_int_set(source_lines: List[str]) -> Set[int]:
    ret: Set[int] = set()
    for line in source_lines:
        for item in line.split(","):
            if "-" in item:
                low, high = item.split("-")
                ret.update(list(range(int(low), int(high) + 1)))
            else:
                ret.add(int(item))
    return ret


def _to_str_set(source_lines: List[str]) -> Set[str]:
    return set(source_lines)


def _to_str_dict(source_lines: List[str]) -> Dict[str, str]:
    ret: Dict[str, str] = {}
    for line in source_lines:
        key, value = line.split(" -> ")
        ret[key] = value
    return ret


class AutoTagSettings:
    def __init__(
        self,
        tagged_post_ids: Set[int] = None,
        untagged_post_ids: Set[int] = None,
        banned_tags: Set[str] = None,
        banned_tag_regexes: Set[str] = None,
        tag_map: Dict[str, str] = None,
        tag_category_map: Dict[str, str] = None,
    ) -> None:
        self._tagged_post_ids = tagged_post_ids or set()
        self._untagged_post_ids = untagged_post_ids or set()
        self._banned_tags: Set[str] = banned_tags or set()
        self._banned_tag_regexes: Set[str] = banned_tag_regexes or set()
        self._tag_map: Dict[str, str] = tag_map or {}
        self._tag_category_map: Dict[str, str] = tag_category_map or {}

    def set_tag_alias(self, tag_name: str, target_tag_name: str) -> None:
        self._tag_map[tag_name] = target_tag_name

    def ban_tag(self, tag_name: str) -> None:
        self._banned_tags.add(tag_name)

    def unban_tag(self, tag_name: str) -> None:
        self._banned_tags.discard(tag_name)

    def mark_as_tagged(self, post_id: int) -> None:
        self._tagged_post_ids.add(post_id)
        self._untagged_post_ids.discard(post_id)

    def mark_as_untagged(self, post_id: int) -> None:
        self._untagged_post_ids.add(post_id)
        self._tagged_post_ids.discard(post_id)

    def get_processed_post_ids(self) -> Set[int]:
        return self._tagged_post_ids | self._untagged_post_ids

    def get_tagged_post_ids(self) -> Set[int]:
        return self._tagged_post_ids

    def get_untagged_post_ids(self) -> Set[int]:
        return self._untagged_post_ids

    def translate_tag(self, tag_name: str) -> str:
        if tag_name in self._tag_map:
            return self._tag_map[tag_name]
        return tag_name

    def translate_tag_category(self, tag_category: str) -> str:
        if tag_category in self._tag_category_map:
            return self._tag_category_map[tag_category]
        return tag_category

    def is_tag_banned(self, tag_name: str) -> bool:
        if tag_name in self._banned_tags:
            return True
        for banned_regex in self._banned_tag_regexes:
            if re.match(banned_regex, tag_name, re.I):
                return True
        return False

    def serialize(self) -> str:
        sections = [
            (SECTION_TAGGED_POST_IDS, _from_int_set(self._tagged_post_ids)),
            (
                SECTION_UNTAGGED_POST_IDS,
                _from_int_set(self._untagged_post_ids),
            ),
            (
                SECTION_BANNED_TAG_REGEXES,
                _from_str_set(self._banned_tag_regexes),
            ),
            (SECTION_BANNED_TAGS, _from_str_set(self._banned_tags)),
            (SECTION_TAG_MAP, _from_str_dict(self._tag_map)),
            (SECTION_TAG_CATEGORY_MAP, _from_str_dict(self._tag_category_map)),
        ]

        return "\n\n".join(
            "\n".join(
                ["--- {} ---".format(section_title)]
                + [line for line in section_lines if line]
            )
            for (section_title, section_lines) in sections
        )

    def save(self, target_path: Path) -> None:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(self.serialize())


def deserialize(text: str) -> AutoTagSettings:
    iterator = iter(enumerate(text.split("\n")))
    sections: Dict[str, List[str]] = {}
    current_section_title: Optional[str] = None
    for i, line in iterator:
        if not line:
            continue
        if line.startswith("---"):
            current_section_title = line.strip("-").strip()
            sections[current_section_title] = []
        else:
            assert current_section_title is not None
            sections[current_section_title].append(line)

    try:
        return AutoTagSettings(
            tagged_post_ids=_to_int_set(sections[SECTION_TAGGED_POST_IDS]),
            untagged_post_ids=_to_int_set(sections[SECTION_UNTAGGED_POST_IDS]),
            banned_tag_regexes=(
                _to_str_set(sections[SECTION_BANNED_TAG_REGEXES])
            ),
            banned_tags=_to_str_set(sections[SECTION_BANNED_TAGS]),
            tag_map=_to_str_dict(sections[SECTION_TAG_MAP]),
            tag_category_map=_to_str_dict(sections[SECTION_TAG_CATEGORY_MAP]),
        )
    except KeyError as ex:
        raise ValueError("Missing section {}".format(ex.args[0]))


def load(source_path: Path) -> AutoTagSettings:
    if not source_path.exists():
        return AutoTagSettings()
    return deserialize(source_path.read_text())
