"""Render every consumer's colors from one palette.

cfg/wezterm/colors says what a color is, roles.toml says what it is for, and
each consumer's *.tmpl says how it wants them spelled: {{text.bright|zsh}}.
"""

import re
import tomllib
from dataclasses import dataclass, field
from functools import cache
from pathlib import Path
from typing import Any, Callable

from libdotfiles.util import HOME_DIR

THEMES = ("light", "dark")

CLAUDE_SLUG = "dash"
CLAUDE_THEME = f"custom:{CLAUDE_SLUG}"

CFG_DIR = Path(__file__).resolve().parents[1]
MARKER_PATH = HOME_DIR / ".config" / "theme"
THEME_DIR = HOME_DIR / ".config" / "theme.d"
ROLES_PATH = CFG_DIR / "theme" / "roles.toml"
PALETTE_PATHS = {
    theme: CFG_DIR / "wezterm" / "colors" / f"dash_{theme}.toml"
    for theme in THEMES
}

PLACEHOLDER = re.compile(r"\{\{\s*([\w.]+)\s*(?:\|\s*(\w+)\s*)?\}\}")


def current_theme(default: str = "light") -> str:
    if MARKER_PATH.exists():
        theme = MARKER_PATH.read_text().strip()
        if theme in THEMES:
            return theme
    return default


@dataclass
class Role:
    light: str
    dark: str
    attrs: list[str] = field(default_factory=list)

    def color(self, theme: str) -> str:
        return self.light if theme == "light" else self.dark


@cache
def load_palette(theme: str) -> dict[int | str, str]:
    """Every palette entry in one theme, by index and by "fg"/"bg"."""
    with PALETTE_PATHS[theme].open("rb") as handle:
        colors = tomllib.load(handle)["colors"]
    palette: dict[int | str, str] = {
        int(key): str(value) for key, value in colors["indexed"].items()
    }
    for index, color in enumerate(colors["ansi"]):
        palette[index] = str(color)
    for index, color in enumerate(colors["brights"]):
        palette[index + 8] = str(color)
    palette["fg"] = str(colors["foreground"])
    palette["bg"] = str(colors["background"])
    return palette


def resolve_color(spec: Any, theme: str, where: str) -> str:
    """A palette index, a literal #rrggbb, or "fg"/"bg", always lowercased.

    Lowercase because tmux expands styles as formats, where #F and #D are
    substitutions that silently eat the rest of the style.
    """
    palette = load_palette(theme)
    if isinstance(spec, bool):  # bool is an int, and never a color
        raise ValueError(f"{where}: {spec!r} is not a color")
    if isinstance(spec, int):
        if spec not in palette:
            raise KeyError(f"{where}: palette has no entry {spec}")
        return palette[spec].lower()
    if isinstance(spec, str):
        if spec in ("fg", "bg"):
            return palette[spec].lower()
        if re.fullmatch(r"#[0-9a-fA-F]{6}", spec):
            return spec.lower()
    raise ValueError(f"{where}: don't know how to resolve {spec!r}")


def resolve_role(spec: Any, where: str) -> Role:
    """A bare spec, or a table giving per-theme specs and attrs."""
    if isinstance(spec, dict):
        attrs = list(spec.get("attrs", []))
        per_theme = {
            theme: spec.get(theme, spec.get("value")) for theme in THEMES
        }
        if any(value is None for value in per_theme.values()):
            raise ValueError(f"{where}: needs `value`, or both light and dark")
    else:
        attrs = []
        per_theme = dict.fromkeys(THEMES, spec)
    return Role(
        light=resolve_color(per_theme["light"], "light", where),
        dark=resolve_color(per_theme["dark"], "dark", where),
        attrs=attrs,
    )


def load_roles() -> dict[str, Role]:
    """Flatten roles.toml into dotted names: `surface.raised` and friends."""
    with ROLES_PATH.open("rb") as handle:
        tree = tomllib.load(handle)
    roles: dict[str, Role] = {}

    def walk(node: dict[str, Any], prefix: str) -> None:
        for key, value in node.items():
            name = f"{prefix}.{key}" if prefix else key
            keys = value.keys() if isinstance(value, dict) else set()
            if isinstance(value, dict) and not (
                keys & {"value", "light", "dark", "attrs"}
            ):
                walk(value, name)
            else:
                roles[name] = resolve_role(value, name)

    walk(tree, "")
    return roles


def to_rgb(color: str) -> tuple[int, int, int]:
    value = color.lstrip("#")
    return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)


FILTERS: dict[str, Callable[[Role, str], str]] = {
    "hex": lambda role, theme: role.color(theme),
    "sgr": lambda role, theme: "38;2;%d;%d;%d" % to_rgb(role.color(theme)),
    "sgrbg": lambda role, theme: "48;2;%d;%d;%d" % to_rgb(role.color(theme)),
    "zsh": lambda role, theme: (
        ("%B" if "bold" in role.attrs else "") + f"%F{{{role.color(theme)}}}"
    ),
    "attrs": lambda role, theme: " ".join(role.attrs),
}


def render(template: str, roles: dict[str, Role], theme: str) -> str:
    def substitute(match: re.Match[str]) -> str:
        name, filter_name = match[1], match[2] or "hex"
        if name == "theme":  # the one thing that isn't a color
            return theme
        if name not in roles:
            raise KeyError(f"template asks for unknown role {name!r}")
        if filter_name not in FILTERS:
            raise KeyError(f"{name}: unknown filter {filter_name!r}")
        return FILTERS[filter_name](roles[name], theme)

    return PLACEHOLDER.sub(substitute, template)


def generate(target_dir: Path = THEME_DIR) -> None:
    """Render every consumer's template, for both themes, into target_dir."""
    target_dir.mkdir(parents=True, exist_ok=True)
    roles = load_roles()
    for template in sorted(CFG_DIR.glob("**/*.tmpl")):
        text = template.read_text()
        name = template.name.removesuffix(".tmpl")
        for theme in THEMES:
            (target_dir / f"{theme}.{name}").write_text(
                render(text, roles, theme)
            )


# rendered name -> the one path that consumer reads, for the consumers that
# can't pick a fragment at runtime: git run from outside zsh, and Claude Code
INSTALLED = {
    "colors.gitconfig": THEME_DIR / "current.gitconfig",
    "claude.json": HOME_DIR / ".claude" / "themes" / f"{CLAUDE_SLUG}.json",
}


def install_theme(theme: str, target_dir: Path = THEME_DIR) -> None:
    for name, target in INSTALLED.items():
        if target.parent.is_dir():
            target.write_text((target_dir / f"{theme}.{name}").read_text())
