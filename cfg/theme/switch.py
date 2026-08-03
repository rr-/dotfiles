"""Switch this machine between the light and dark theme.

Installed onto PATH as `theme` by cfg/theme/__main__.py.
"""

import argparse
import os
import re
from pathlib import Path
from subprocess import DEVNULL, TimeoutExpired, run

from cfg.theme import osc
from cfg.theme.render import (
    MARKER_PATH,
    THEMES,
    current_theme,
    generate,
    install_theme,
)
from libdotfiles.util import HOME_DIR


def quiet(*command: object) -> None:
    """Nothing we poke at is worth failing the switch over."""
    try:
        run(
            [str(word) for word in command],
            stdout=DEVNULL,
            stderr=DEVNULL,
            timeout=5,
            check=False,
        )
    except (OSError, TimeoutExpired):
        pass


def update_wezterm_config(theme: str) -> None:
    """Only ever reaches a wezterm running on this machine.

    Over ssh the terminal is on the other end and reads its own config, which
    is what cfg/theme/osc.py is for; leave this for the local case.
    """
    path = HOME_DIR / ".config" / "wezterm" / "runtime.lua"
    if not path.exists():
        return
    path.write_text(
        re.sub(r"((dash|stardust)[_-])\w+", rf"\1{theme}", path.read_text())
    )


def update_theme_marker(theme: str) -> None:
    """Record the theme every other program reads back out."""
    MARKER_PATH.parent.mkdir(parents=True, exist_ok=True)
    MARKER_PATH.write_text(theme + "\n")


def update_running_nvim(theme: str) -> None:
    # --headless, or the client spends a second waiting on the terminal
    runtime_dir = Path(
        os.environ.get("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}")
    )
    for socket in sorted(runtime_dir.glob("nvim.*")):
        quiet(
            "nvim",
            "--headless",
            "--server",
            socket,
            "--remote-expr",
            f"execute('set background={theme}')",
        )


def update_running_tmux(theme: str) -> None:
    # setenv as well: a tmux server hands every pane it makes afterwards the
    # environment it was started with, so panes opened later announce the old
    # theme to everything in them that doesn't read the marker itself
    quiet("tmux", "setenv", "-g", "THEME", theme)
    quiet(
        "tmux",
        "source-file",
        HOME_DIR / ".config" / "theme.d" / f"{theme}.colors.conf",
    )


def update_running_zsh() -> None:
    # WINCH rather than USR1: shells that predate this redraw instead of dying
    quiet("pkill", "-WINCH", "-x", "-u", os.getuid(), "zsh")


def update_gtk_config(theme: str) -> None:
    gtk_theme = "Arc-Dark" if theme == "dark" else "Arc"
    for path, header in [
        (HOME_DIR / ".gtkrc-2.0", ""),
        (HOME_DIR / ".config" / "gtk-3.0" / "settings.ini", "[Settings]"),
    ]:
        old = path.read_text() if path.exists() else header
        lines = [
            line
            for line in old.splitlines()
            if not line.startswith("gtk-theme-name")
        ]
        lines.append(f'gtk-theme-name="{gtk_theme}"')
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(lines) + "\n")
    run(
        [
            "gsettings",
            "set",
            "org.gnome.desktop.interface",
            "gtk-key-theme",
            gtk_theme,
        ],
        check=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Switch this machine between the light and dark theme, "
        "or print the theme it is on."
    )
    parser.add_argument("theme", choices=THEMES, nargs="?")
    theme = parser.parse_args().theme
    if theme is None:
        print(current_theme("unknown"))
        return
    # rendering here rather than at install time means editing a role shows up
    # on the next switch
    generate()
    osc.generate()
    install_theme(theme)
    update_wezterm_config(theme)
    osc.repaint(theme)
    update_theme_marker(theme)
    update_running_nvim(theme)
    update_running_tmux(theme)
    update_running_zsh()
    update_gtk_config(theme)


if __name__ == "__main__":
    main()
