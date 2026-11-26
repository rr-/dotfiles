"""Syntax highlighting with pygments, and word-level emphasis."""

import dataclasses as dc
import difflib
import re
from pathlib import Path

from pygments.lexer import Lexer
from pygments.lexers import get_lexer_by_name, get_lexer_for_filename
from pygments.token import _TokenType
from pygments.util import ClassNotFound

from .model import FileDiff

LEXER_OPTIONS = {"stripnl": False, "ensurenl": True}


def lexer_from_shebang(line: str) -> Lexer | None:
    if not line.startswith("#!"):
        return None
    words = [w for w in line[2:].split() if not w.startswith("-")]
    words = [w for w in words if "=" not in w]
    if words and Path(words[0]).name == "env":
        words = words[1:]
    if not words:
        return None
    name = re.sub(r"[\d.]+$", "", Path(words[0]).name)
    name = {"uv": "python", "node": "javascript"}.get(name, name)
    try:
        return get_lexer_by_name(name, **LEXER_OPTIONS)
    except ClassNotFound:
        return None


def pick_lexer(f: FileDiff, root: Path | None) -> Lexer | None:
    try:
        return get_lexer_for_filename(f.path, **LEXER_OPTIONS)
    except ClassNotFound:
        pass
    for hunk in f.hunks:
        for line in hunk.lines:
            if (line.new == 1 and line.kind == "+") or line.old == 1:
                return lexer_from_shebang(line.text)
    if root is not None:
        try:
            with (root / f.path).open(errors="replace") as handle:
                return lexer_from_shebang(handle.readline())
        except OSError:
            pass
    return None


def split_token_lines(
    tokens: list[tuple[_TokenType, str]], count: int
) -> list[list[tuple[_TokenType, str]]]:
    out: list[list[tuple[_TokenType, str]]] = [[]]
    for ttype, value in tokens:
        for i, part in enumerate(value.split("\n")):
            if i:
                out.append([])
            if part:
                out[-1].append((ttype, part))
    return (out + [[]] * count)[:count]


WORD_RE = re.compile(r"\w+|\s+|[^\w\s]")


def emph_ranges(
    a: str, b: str
) -> tuple[list[tuple[int, int]], list[tuple[int, int]]] | None:
    """The spans that differ between a removed line and its replacement."""
    wa = [(m.start(), m.end()) for m in WORD_RE.finditer(a)]
    wb = [(m.start(), m.end()) for m in WORD_RE.finditer(b)]
    matcher = difflib.SequenceMatcher(
        None, [a[s:e] for s, e in wa], [b[s:e] for s, e in wb], autojunk=False
    )
    if matcher.ratio() < 0.4:
        return None
    ra: list[tuple[int, int]] = []
    rb: list[tuple[int, int]] = []
    for op, i1, i2, j1, j2 in matcher.get_opcodes():
        if op == "equal":
            continue
        if i1 < i2:
            ra.append((wa[i1][0], wa[i2 - 1][1]))
        if j1 < j2:
            rb.append((wb[j1][0], wb[j2 - 1][1]))
    return ra, rb


@dc.dataclass
class Highlight:
    tokens: dict[tuple[int, int], list[tuple[_TokenType, str]]]
    emph: dict[tuple[int, int], list[tuple[int, int]]]


def highlight_file(f: FileDiff, root: Path | None) -> Highlight:
    tokens: dict[tuple[int, int], list[tuple[_TokenType, str]]] = {}
    emph: dict[tuple[int, int], list[tuple[int, int]]] = {}

    lexer = None if f.binary else pick_lexer(f, root)
    if lexer is not None:
        # Each side reads as one stretch of code, so a string or comment that
        # opens in one line still colors the lines after it.
        for kinds in (" +", "-"):
            keys = [
                (hi, li)
                for hi, hunk in enumerate(f.hunks)
                for li, line in enumerate(hunk.lines)
                if line.kind in kinds
            ]
            if not keys:
                continue
            source = "\n".join(
                f.hunks[hi].lines[li].text.replace("\r", " ")
                for hi, li in keys
            )
            lines = split_token_lines(
                list(lexer.get_tokens(source)), len(keys)
            )
            tokens.update(zip(keys, lines))

    for hi, hunk in enumerate(f.hunks):
        lines = hunk.lines
        i = 0
        while i < len(lines):
            if lines[i].kind != "-":
                i += 1
                continue
            j = i
            while j < len(lines) and lines[j].kind == "-":
                j += 1
            k = j
            while k < len(lines) and lines[k].kind == "+":
                k += 1
            for a, b in zip(range(i, j), range(j, k)):
                ranges = emph_ranges(lines[a].text, lines[b].text)
                if ranges:
                    emph[hi, a], emph[hi, b] = ranges
            i = k
    return Highlight(tokens, emph)
