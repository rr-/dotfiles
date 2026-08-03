"""Hand the terminal a palette it cannot read off this machine.

Every other consumer here reads its colors out of a file this box writes. The
terminal is the one that can't: over ssh it is a wezterm on somebody's windows,
painting ANSI 0-15, the default background and the cursor out of a scheme file
we will never touch. Escapes down the tty are the only channel we have to it.

Two senders, because one is not enough. cfg/theme/switch.py repaints every
terminal attached right now, so a switch lands on the panes you already have;
cfg/zsh/zshrc emits the same bytes on the way up, so a pane opened afterwards
stops inheriting whatever the terminal booted with.
"""

import os
from pathlib import Path
from subprocess import TimeoutExpired, run

from cfg.theme.render import (
    THEME_DIR,
    THEMES,
    Role,
    load_palette,
    load_roles,
    to_rgb,
)

OSC = "\033]"
# BEL rather than ST: every terminal that takes OSC at all takes BEL, and it
# carries one fewer escape through the tmux wrapper below.
BEL = "\a"

# One sequence per batch rather than one per color - but not one sequence for
# all 256, because a terminal is entitled to a limit on how long an OSC runs.
BATCH = 16

# the terminal's cursor, from the role nvim already paints its own with
CURSOR_ROLE = "editor.cursor_bg"


def x_color(color: str) -> str:
    """#rrggbb is legal in an OSC, but rgb:rr/gg/bb is what X means."""
    return "rgb:%02x/%02x/%02x" % to_rgb(color)


def payload(theme: str) -> str:
    """The whole palette as escapes: 256 indices, fg, bg, cursor."""
    palette = load_palette(theme)
    roles: dict[str, Role] = load_roles()
    indices = sorted(key for key in palette if isinstance(key, int))

    pieces = []
    for start in range(0, len(indices), BATCH):
        batch = indices[start : start + BATCH]
        body = ";".join(
            f"{index};{x_color(palette[index])}" for index in batch
        )
        pieces.append(f"{OSC}4;{body}{BEL}")
    pieces.append(f"{OSC}10;{x_color(palette['fg'])}{BEL}")
    pieces.append(f"{OSC}11;{x_color(palette['bg'])}{BEL}")
    if CURSOR_ROLE in roles:
        cursor = x_color(roles[CURSOR_ROLE].color(theme))
        pieces.append(f"{OSC}12;{cursor}{BEL}")
    return "".join(pieces)


def through_tmux(text: str) -> str:
    """Wrap escapes aimed past tmux at the terminal behind it.

    tmux parses an OSC 4 itself rather than forwarding it, so a shell inside a
    pane has to tunnel. Needs `allow-passthrough on`, which cfg/tmux/tmux.conf
    sets, and the doubled escapes are how the wrapper quotes its own payload.
    """
    return "\033Ptmux;" + text.replace("\033", "\033\033") + "\033\\"


def terminals() -> list[str]:
    """Every tty a repaint should land on.

    Never a tmux pane's own tty: writing there hands the bytes to tmux, which
    parses them instead of passing them on. An attached client's tty is the ssh
    pty itself, so the escapes reach the terminal with nobody in between.
    """
    ttys: list[str] = []
    try:
        clients = run(
            ["tmux", "list-clients", "-F", "#{client_tty}"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        ttys.extend(clients.stdout.split())
    except (OSError, TimeoutExpired):
        pass  # no tmux on this machine, or no server running
    if "TMUX" not in os.environ:
        for fd in (1, 2):
            try:
                ttys.append(os.ttyname(fd))
                break
            except OSError:
                continue
    return list(dict.fromkeys(ttys))


def repaint(theme: str) -> None:
    """Push the palette at every terminal we can reach right now."""
    text = payload(theme)
    for tty in terminals():
        try:
            with open(tty, "w") as handle:
                handle.write(text)
        except OSError:
            pass  # a client that detached between listing it and writing to it


def generate(target_dir: Path = THEME_DIR) -> None:
    """Both themes' palettes, as bytes a starting shell can print."""
    target_dir.mkdir(parents=True, exist_ok=True)
    for theme in THEMES:
        text = payload(theme)
        (target_dir / f"{theme}.palette.osc").write_text(text)
        (target_dir / f"{theme}.palette.tmux.osc").write_text(
            through_tmux(text)
        )
