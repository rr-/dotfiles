"""Editing the line in the prompt, with the keys of readline."""

import re

WORD_RE = re.compile(r"\w")


def word_left(text: str, pos: int) -> int:
    """The start of the word before pos, as M-b goes."""
    while pos > 0 and not WORD_RE.match(text[pos - 1]):
        pos -= 1
    while pos > 0 and WORD_RE.match(text[pos - 1]):
        pos -= 1
    return pos


def word_right(text: str, pos: int) -> int:
    """The end of the word after pos, as M-f goes."""
    while pos < len(text) and not WORD_RE.match(text[pos]):
        pos += 1
    while pos < len(text) and WORD_RE.match(text[pos]):
        pos += 1
    return pos


def edit_line(text: str, pos: int, key: str) -> tuple[str, int] | None:
    """The line and cursor after a key, or None for a key it leaves alone."""
    match key:
        case "left" | "C-b":
            return text, max(0, pos - 1)
        case "right" | "C-f":
            return text, min(len(text), pos + 1)
        case "home" | "C-a":
            return text, 0
        case "end":
            return text, len(text)
        case "M-b" | "C-left":
            return text, word_left(text, pos)
        case "M-f" | "C-right":
            return text, word_right(text, pos)
        case "backspace" | "C-h":
            if pos == 0:
                return text, pos
            return text[: pos - 1] + text[pos:], pos - 1
        case "delete" | "C-d":
            return text[:pos] + text[pos + 1 :], pos
        case "C-w":
            # as in a shell: back to the last whitespace
            start = len(re.sub(r"\S*\s*$", "", text[:pos]))
            return text[:start] + text[pos:], start
        case "M-backspace":
            start = word_left(text, pos)
            return text[:start] + text[pos:], start
        case "M-d":
            end = word_right(text, pos)
            return text[:pos] + text[end:], pos
        case "C-u":
            return text[pos:], 0
        case "C-k":
            return text[:pos], pos
    if len(key) == 1 and key.isprintable():
        return text[:pos] + key + text[pos:], pos + 1
    return None
