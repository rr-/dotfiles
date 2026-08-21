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


def gtk_theme(theme: str) -> str:
    return "Adwaita-dark" if theme == "dark" else "Adwaita"


def update_wallpaper(theme: str) -> None:
    """Point ~/.wallpaper.EXT at this theme's ~/.wallpaper-THEME.EXT."""
    sources: list[Path] = []
    for source in sorted(HOME_DIR.glob(f".wallpaper-{theme}.*")):
        link = HOME_DIR / f".wallpaper{source.suffix}"
        if link.exists() and not link.is_symlink():
            continue
        pending = link.with_name(link.name + ".new")
        pending.unlink(missing_ok=True)
        pending.symlink_to(source)
        pending.replace(link)
        sources.append(source)
    if sources:
        # the file and not the link: xfdesktop repaints on the property
        # changing, and the link's path is the same either way
        point_xfdesktop_at(sources[0])


def point_xfdesktop_at(image: Path) -> None:
    """Every monitor and workspace, since which one draws the desktop in
    front of you depends on what is plugged in and which workspace is up."""
    try:
        listing = run(
            ["xfconf-query", "-c", "xfce4-desktop", "-l"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        ).stdout
    except (OSError, TimeoutExpired):
        return  # no xfconf here
    for prop in listing.split():
        if prop.endswith("/last-image"):
            quiet(
                "xfconf-query", "-c", "xfce4-desktop", "-p", prop, "-s", image
            )


def update_xfce_theme(theme: str) -> None:
    """xfsettingsd overrides the gtk config files, so it needs telling too."""
    quiet(
        "xfconf-query",
        "-c",
        "xsettings",
        "-p",
        "/Net/ThemeName",
        "-s",
        gtk_theme(theme),
    )
    # the panel pins itself to the dark variant of whatever theme it is
    # given, so on a light theme it is the one thing left dark
    quiet(
        "xfconf-query",
        "-c",
        "xfce4-panel",
        "-p",
        "/panels/dark-mode",
        "-t",
        "bool",
        "-s",
        "true" if theme == "dark" else "false",
        "--create",
    )


def update_gtk_config(theme: str) -> None:
    # gtk3's ini parser takes the quotes gtk2 wants for part of the name
    for path, header, name in [
        (HOME_DIR / ".gtkrc-2.0", "", f'"{gtk_theme(theme)}"'),
        (
            HOME_DIR / ".config" / "gtk-3.0" / "settings.ini",
            "[Settings]",
            gtk_theme(theme),
        ),
    ]:
        old = path.read_text() if path.exists() else header
        lines = [
            line
            for line in old.splitlines()
            if not line.startswith("gtk-theme-name")
        ]
        lines.append(f"gtk-theme-name={name}")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(lines) + "\n")
    # what chromium and electron ask the desktop portal for; a gtk theme name
    # means nothing to them
    quiet(
        "gsettings",
        "set",
        "org.gnome.desktop.interface",
        "color-scheme",
        "prefer-dark" if theme == "dark" else "default",
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
    update_xfce_theme(theme)
    update_wallpaper(theme)


if __name__ == "__main__":
    main()
