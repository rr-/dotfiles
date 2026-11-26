"""Colors from cfg/theme/roles.toml, turned into SGR sequences."""

import os
import tomllib
from functools import cache
from pathlib import Path
from typing import NamedTuple

from pygments.token import (
    Comment,
    Error,
    Generic,
    Keyword,
    Name,
    Number,
    Operator,
    String,
    Token,
    _TokenType,
)

CFG_DIR = Path(__file__).resolve().parents[2] / "cfg"
ROLES_PATH = CFG_DIR / "theme/roles.toml"

type Color = int | str | None


class Style(NamedTuple):
    fg: Color = None
    bg: Color = None
    bold: bool = False
    rev: bool = False


PLAIN = Style()


def load_roles() -> dict:
    try:
        with ROLES_PATH.open("rb") as handle:
            return tomllib.load(handle)
    except OSError:
        return {}


ROLES = load_roles()
THEME = os.environ.get("THEME", "dark")
# a variant of light takes light's spec for whatever it doesn't name itself
BASE = "light" if THEME.startswith("light") else "dark"


def load_palette() -> dict[int | str, str]:
    """The theme's palette, so indices go out as rgb: a terminal that ignores
    the OSC 4 remap - Termius - would paint them from its own palette."""
    try:
        with (CFG_DIR / f"wezterm/colors/dash_{THEME}.toml").open("rb") as f:
            colors = tomllib.load(f)["colors"]
    except (OSError, KeyError):
        return {}
    palette: dict[int | str, str] = {
        int(key): value for key, value in colors.get("indexed", {}).items()
    }
    for index, color in enumerate(colors.get("ansi", [])):
        palette[index] = color
    for index, color in enumerate(colors.get("brights", [])):
        palette[index + 8] = color
    palette["fg"] = colors.get("foreground")
    return palette


PALETTE = load_palette()
FALLBACK_ROLES: dict[str, Color] = {
    "text.faint": 242,
    "text.muted": 7,
    "text.inverse": 232,
    "surface.raised": 235,
    "surface.overlay": 238,
    "accent.primary": 39,
    "accent.info": 110,
    "accent.link": 14,
    "state.error": 203,
    "state.warning": 173,
    "state.success": 150,
    "diff.add.bg": 64,
    "diff.add.emph": 70,
    "diff.add.accent": 10,
    "diff.del.bg": 130,
    "diff.del.emph": 166,
    "diff.del.accent": 9,
    "diff.meta.fg": 255,
    "diff.meta.bg": 234,
    "diff.frag.fg": 255,
    "diff.frag.bg": 23,
    "file.dir": 4,
}


@cache
def role(name: str) -> Color:
    value = ROLES
    for key in name.split("."):
        value = value.get(key) if isinstance(value, dict) else None
    if value is None:
        value = FALLBACK_ROLES.get(name)
    if isinstance(value, dict):
        value = value.get(
            THEME, value.get(BASE, value.get("value", value.get("dark")))
        )
    if value == "fg":
        return PALETTE.get("fg")
    if value == "bg":
        return None
    if isinstance(value, int) and not isinstance(value, bool):
        return PALETTE.get(value, value)
    return value


def color_sgr(color: Color, base: int) -> str:
    if isinstance(color, int):
        return f"{base + 8};5;{color}"
    if isinstance(color, str) and color.startswith("#"):
        r, g, b = (int(color[i : i + 2], 16) for i in (1, 3, 5))
        return f"{base + 8};2;{r};{g};{b}"
    return str(base + 9)


@cache
def sgr(style: Style) -> str:
    parts = ["0"]
    if style.bold:
        parts.append("1")
    if style.rev:
        parts.append("7")
    parts.append(color_sgr(style.fg, 30))
    parts.append(color_sgr(style.bg, 40))
    return f"\x1b[{';'.join(parts)}m"


TOKEN_ROLES: dict[_TokenType, str | None] = {
    Token: None,
    Comment: "comment",
    Comment.Hashbang: "comment",
    Comment.Preproc: "preproc",
    Comment.PreprocFile: "string",
    Keyword: "keyword",
    Keyword.Constant: "constant",
    Keyword.Namespace: "preproc",
    Keyword.Type: "type",
    Operator.Word: "keyword",
    Name.Builtin: "type_alt",
    Name.Builtin.Pseudo: "constant",
    Name.Class: "type",
    Name.Constant: "constant",
    Name.Decorator: "preproc",
    Name.Entity: "constant_alt",
    Name.Exception: "type",
    Name.Function: "function",
    Name.Label: "special_key",
    Name.Tag: "statement",
    Name.Attribute: "type",
    String: "string",
    String.Affix: "keyword",
    String.Char: "character",
    String.Doc: "doc",
    String.Escape: "constant_alt",
    String.Interpol: "constant_alt",
    String.Regex: "constant_alt",
    Number: "number",
    Generic.Heading: "statement",
    Generic.Subheading: "type",
    Generic.Inserted: "type_alt",
    Generic.Deleted: "keyword",
    Error: "keyword",
}


@cache
def token_color(ttype: _TokenType) -> Color:
    while ttype not in TOKEN_ROLES:
        ttype = ttype.parent
    name = TOKEN_ROLES[ttype]
    return role(f"syntax.{name}") if name else None
