"""One palette, many config formats.

The 256-color palettes in cfg/wezterm/colors say what a color *is*;
cfg/theme/roles.toml says what each color is *for*; and every consumer keeps a
`*.tmpl` next to its own config saying how it wants them written down. This
module is just the substitution pass: `{{role.name}}`, optionally with a
filter for the syntax the consumer speaks - `{{text.bright|zsh}}`,
`{{accent.info|sgr}}`.

The indirection used to be the terminal's job: configs said "colour235" and
the terminal resolved it through the palette we handed it over OSC 4.
Terminals that ignore OSC 4 (PowerShell, conhost) resolved it through their
own palette instead, which is how a status bar ends up dark on a light theme.
Resolving it here means every config ships real rgb and nothing has to be
written down twice.
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

MARKER_PATH = HOME_DIR / ".config" / "theme"


def current_theme(default: str = "light") -> str:
    """What theme(1) last recorded for the programs that can't ask."""
    if MARKER_PATH.exists():
        theme = MARKER_PATH.read_text().strip()
        if theme in THEMES:
            return theme
    return default


CFG_DIR = Path(__file__).resolve().parents[1]
THEME_DIR = HOME_DIR / ".config" / "theme.d"
PALETTE_PATHS = {
    theme: CFG_DIR / "wezterm" / "colors" / f"dash_{theme}.toml"
    for theme in THEMES
}
ROLES_PATH = CFG_DIR / "theme" / "roles.toml"

PLACEHOLDER = re.compile(r"\{\{\s*([\w.]+)\s*(?:\|\s*(\w+)\s*)?\}\}")


@dataclass
class Role:
    """One color, in both themes, plus any attributes that travel with it."""

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
    """A spec is a palette index, a literal #rrggbb, or "fg"/"bg".

    Always lowercase, and not only for tidiness: tmux expands the styles it
    embeds in status-format as formats, where # introduces a substitution.
    "#FDFDFD" becomes the window flag followed by "DFDFD" and "#DCDCDC"
    becomes the pane id, which silently drops the style and the alignment
    that came with it. The shortcuts are uppercase, so lowercase hex is safe.
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
    """Turn one roles.toml entry into a Role.

    An entry is either a bare spec - the same index or color in both themes -
    or a table that may give a per-theme spec and a list of attributes.
    """
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
            # a table is a group of roles unless it looks like a role itself
            is_role = isinstance(value, dict) and (
                value.keys() & {"value", "light", "dark", "attrs"}
            )
            if isinstance(value, dict) and not is_role:
                walk(value, name)
            else:
                roles[name] = resolve_role(value, name)

    walk(tree, "")
    return roles


def to_rgb(color: str) -> tuple[int, int, int]:
    value = color.lstrip("#")
    return (
        int(value[0:2], 16),
        int(value[2:4], 16),
        int(value[4:6], 16),
    )


# how each consumer wants a color spelled out
FILTERS: dict[str, Callable[[Role, str], str]] = {
    # plain #rrggbb - tmux, git, lua, json, fzf
    "hex": lambda role, theme: role.color(theme),
    # the truecolor half of an SGR sequence, for hand-written escapes
    "sgr": lambda role, theme: "38;2;%d;%d;%d" % to_rgb(role.color(theme)),
    "sgrbg": lambda role, theme: "48;2;%d;%d;%d" % to_rgb(role.color(theme)),
    # a zsh prompt escape, bold included when the role asks for it
    "zsh": lambda role, theme: (
        ("%B" if "bold" in role.attrs else "") + f"%F{{{role.color(theme)}}}"
    ),
    # whatever attributes the role carries, in the order they were written
    "attrs": lambda role, theme: " ".join(role.attrs),
}


def render(template: str, roles: dict[str, Role], theme: str) -> str:
    """Substitute every {{role}} / {{role|filter}} in one template."""

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


def find_templates() -> list[Path]:
    return sorted(CFG_DIR.glob("**/*.tmpl"))


def output_name(template: Path, theme: str) -> str:
    """cfg/tmux/config/tmux.conf.tmpl -> light.tmux.conf"""
    return f"{theme}.{template.name.removesuffix('.tmpl')}"


def is_stale(target_dir: Path) -> bool:
    """Has anything we render from changed since we last rendered it?"""
    # this module counts as an input: it decides how the values come out
    inputs = [
        Path(__file__),
        ROLES_PATH,
        *PALETTE_PATHS.values(),
        *find_templates(),
    ]
    outputs = [
        target_dir / output_name(template, theme)
        for template in find_templates()
        for theme in THEMES
    ]
    if not all(output.exists() for output in outputs):
        return True
    newest_input = max(path.stat().st_mtime for path in inputs)
    return newest_input > min(path.stat().st_mtime for path in outputs)


def generate(target_dir: Path = THEME_DIR, force: bool = False) -> None:
    """Render every consumer's template, for both themes, into target_dir."""
    target_dir.mkdir(parents=True, exist_ok=True)
    if not (force or is_stale(target_dir)):
        return
    roles = load_roles()
    for template in find_templates():
        text = template.read_text()
        for theme in THEMES:
            (target_dir / output_name(template, theme)).write_text(
                render(text, roles, theme)
            )


# rendered name -> the one path that consumer reads
INSTALLED = {
    "colors.gitconfig": THEME_DIR / "current.gitconfig",
    "claude.json": HOME_DIR / ".claude" / "themes" / f"{CLAUDE_SLUG}.json",
}


def install_theme(theme: str, target_dir: Path = THEME_DIR) -> None:
    """Point the consumers that can't choose at runtime at one theme.

    zsh and tmux pick the fragment matching the terminal they're talking to,
    but git run from outside zsh, and Claude Code, only get to see whatever
    this machine last switched to. Claude reads its theme name at startup, so
    the name stays fixed and this file's `base` is what changes - it watches
    the directory, and repaints in place.
    """
    for name, target in INSTALLED.items():
        if not target.parent.is_dir():
            continue
        target.write_text((target_dir / f"{theme}.{name}").read_text())
