# Marcin Kurczewski (2017) - refactors etc.
# Herman Schaaf (2013) - adaptation for EDICT 2
# Paul Goins (2009) - original script for EDICT 1

# EDICT2 FORMAT:
#
#    KANJI-1;KANJI-2 [KANA-1;KANA-2] /(general information) (see xxxx) gloss/gloss/.../
#    垜;安土;堋 [あずち] /(n) mound on which targets are placed (in archery)/firing mound/EntL2542010/

import typing as t
import re

# Part of speech codes
VALID_POS_CODES = [
    'adj-i',
    'adj-na',
    'adj-no',
    'adj-pn',
    'adj-t',
    'adj-f',
    'adj',
    'adv',
    'adv-to',
    'aux',
    'aux-v',
    'aux-adj',
    'conj',
    'ctr',
    'exp',
    'int',
    'iv',
    'n',
    'n-adv',
    'n-suf',
    'n-pref',
    'n-t',
    'num',
    'pn',
    'pref',
    'prt',
    'suf',
    'v1',
    'v2a-s',
    'v4h',
    'v4r',
    'v5',
    'v5aru',
    'v5b',
    'v5g',
    'v5k',
    'v5k-s',
    'v5m',
    'v5n',
    'v5r',
    'v5r-i',
    'v5s',
    'v5t',
    'v5u',
    'v5u-s',
    'v5uru',
    'v5z',
    'vz',
    'vi',
    'vk',
    'vn',
    'vr',
    'vs',
    'vs-s',
    'vs-i',
    'vt',
]

# Field of application codes
VALID_FOA_CODES = [
    'Buddh',
    'MA',
    'comp',
    'food',
    'geom',
    'ling',
    'math',
    'mil',
    'physics',
    'chem',
    'biol',
]

# Miscellaneous marking codes
VALID_MISC_CODES = [
    'X',
    'abbr',
    'arch',
    'ateji',
    'chn',
    'col',
    'derog',
    'eK',
    'ek',
    'fam',
    'fem',
    'gikun',
    'hon',
    'hum',
    'iK',
    'id',
    'ik',
    'io',
    'm-sl',
    'male',
    'male-sl',
    'oK',
    'obs',
    'obsc',
    'ok',
    'on-mim',
    'poet',
    'pol',
    'rare',
    'sens',
    'sl',
    'uK',
    'uk',
    'vulg',
    'P',
]


# Dialect codes
VALID_DIALECT_CODES = [
    'kyb',
    'osb',
    'ksb',
    'ktb',
    'tsb',
    'thb',
    'tsug',
    'kyu',
    'rkb',
    'nab',
]

_RE_KANA = re.compile(r'\[(.+)\]')
_RE_FIELD_TAGS = re.compile(r'\{(%s)\}' % '|'.join(VALID_FOA_CODES))
_RE_NUMBER_TAG = re.compile(r'\((\d+)\)')
_RE_ANY_TAG = re.compile(r'\(([^)]*)\)')
_RE_RELATED_TAG = re.compile(r'\(See ([^)]*)\)', re.IGNORECASE)
_RE_TAGS = re.compile(
    r'\(((?:%s|[,]+)+)\:?\)'
    % '|'.join(VALID_POS_CODES + VALID_MISC_CODES + VALID_DIALECT_CODES)
)


class EdictJapanese:
    def __init__(
        self,
        kanji: str,
        kana: str,
        kanji_tags: t.Sequence[str],
        kana_tags: t.Sequence[str],
    ) -> None:
        self.kanji = kanji
        self.kana = kana
        self.kanji_tags = kanji_tags
        self.kana_tags = kana_tags


class EdictGlossary:
    def __init__(
        self,
        english: str,
        tags: t.Sequence[str],
        field: t.Optional[str],
        related: t.List[str],
        common: bool = False,
    ) -> None:
        self.english = english
        self.tags = tags
        self.field = field
        self.related = related
        self.common = common
        if 'P' in self.tags:
            self.common = True


class EdictEntry:
    def __init__(
        self,
        glossaries: t.List[EdictGlossary],
        japanese: t.List[EdictJapanese],
        tags: t.Sequence[str],
        ent_seq: t.Optional[str],
        has_audio: bool,
    ) -> None:
        self.glossaries = glossaries
        self.japanese = japanese
        self.tags = tags
        self.ent_seq = ent_seq
        self.has_audio = has_audio


def _extract_tags(
    word: str, expression: t.Pattern
) -> t.Tuple[str, t.Sequence[str]]:
    match = expression.search(word)
    tags: t.List[str] = []
    if match:
        groups = match.groups()
        for group in groups:
            tags += group.split(',')
        word = expression.sub('', word)
    return word, tuple(tags)


def _extract_related(glossaries: str) -> t.Tuple[str, t.Sequence[str]]:
    return _extract_tags(word=glossaries, expression=_RE_RELATED_TAG)


def _extract_fields(glossaries: str) -> t.Tuple[str, t.Sequence[str]]:
    return _extract_tags(word=glossaries, expression=_RE_FIELD_TAGS)


def _get_entry(raw_entry: str) -> EdictEntry:
    raw_words = raw_entry.split(' ')
    raw_kanji = raw_words[0].split(';')
    kana_match = _RE_KANA.match(raw_words[1])
    if kana_match:
        raw_kana = kana_match.group(1).split(';')
    else:
        raw_kana = raw_kanji

    kanji_tagged = [_extract_tags(k, _RE_TAGS) for k in raw_kanji]
    kana_tagged = [_extract_tags(k, _RE_TAGS) for k in raw_kana]

    raw_english = raw_entry.split('/')[1:-2]

    english_word, main_tags = _extract_tags(raw_english[0], _RE_TAGS)
    english = [english_word] + raw_english[1:]

    if english[-1] == '(P)':
        main_tags = tuple(set(list(main_tags) + ['P']))
        english = english[:-1]

    # join numbered entries:
    joined_english: t.List[str] = []
    has_numbers = False
    for word in english:
        clean, number = _extract_tags(word, _RE_NUMBER_TAG)
        clean = clean.strip()
        if number:
            has_numbers = True
            joined_english.append(clean)
        elif has_numbers:
            joined_english[-1] += '/' + clean
        else:
            joined_english.append(clean)
    english = joined_english

    glossaries = []
    for gloss in english:
        clean_gloss, related_words = _extract_related(gloss)
        clean_gloss, tags = _extract_tags(clean_gloss, _RE_TAGS)
        clean_gloss, fields = _extract_fields(clean_gloss)

        if related_words:
            related_words = related_words[0].split(',')
        else:
            related_words = []

        field = fields[0] if fields else None
        clean_gloss = clean_gloss.strip()
        if clean_gloss:
            glossaries.append(
                EdictGlossary(
                    english=clean_gloss,
                    tags=tags,
                    field=field,
                    related=related_words,
                )
            )

    ent_seq = raw_entry.split('/')[-2]

    # entL sequences that end in X have audio clips
    has_audio = ent_seq[-1] == 'X'

    # throw away the entL and X part, keeping only the id
    ent_seq = ent_seq[4:]
    if has_audio:
        ent_seq = ent_seq[:-1]

    japanese: t.List[EdictJapanese] = []
    for kana, ktag in kana_tagged:
        # special case for kana like this: おくび(噯,噯気);あいき(噯気,噫気,噯木)
        kana, matching_kanji = _extract_tags(kana, _RE_ANY_TAG)
        if matching_kanji:
            matching_kanji = matching_kanji[0].split(',')

        for kanji, jtag in kanji_tagged:
            if not matching_kanji or kanji in matching_kanji:
                japanese.append(
                    EdictJapanese(
                        kanji=kanji, kana=kana, kanji_tags=jtag, kana_tags=ktag
                    )
                )

    return EdictEntry(
        japanese=japanese,
        glossaries=glossaries,
        tags=main_tags,
        ent_seq=ent_seq,
        has_audio=has_audio,
    )


def parse(lines: t.Iterable[str]) -> t.Iterable[EdictEntry]:
    for line in lines:
        if line and line[0] != '#':
            yield _get_entry(line)
