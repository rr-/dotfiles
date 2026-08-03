"""Switch this machine between the light and dark theme.

Installed onto PATH as `theme` by cfg/theme/__main__.py.
"""

import argparse
import os
import re
from pathlib import Path
from subprocess import DEVNULL, run

from cfg.theme.render import (
    MARKER_PATH,
    current_theme,
    generate,
    install_theme,
)
from libdotfiles.util import HOME_DIR


def update_generated_colors(theme: str) -> None:
    """Re-render every consumer's colors from cfg/theme/roles.toml.

    Doing it here rather than at install time means editing a role shows up on
    the next switch, and that the files are always in step with the repo.
    """
    generate()
    install_theme(theme)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Switch this machine between the light and dark theme, "
        "or print the theme it is on."
    )
    parser.add_argument("theme", choices=["dark", "light"], nargs="?")
    return parser.parse_args()


def update_wezterm_config(theme: str) -> None:
    config_dir = HOME_DIR / ".config" / "wezterm"
    theme_config_path = config_dir / "runtime.lua"
    theme_config = theme_config_path.read_text()
    theme_config = re.sub(
        r"((dash|stardust)[_-])\w+", rf"\1{theme}", theme_config
    )
    theme_config_path.write_text(theme_config)


def update_theme_marker(theme: str) -> None:
    """Record the theme every other program reads back out."""
    MARKER_PATH.parent.mkdir(parents=True, exist_ok=True)
    MARKER_PATH.write_text(theme + "\n")


def update_running_nvim(theme: str) -> None:
    """Repaint already-running neovim instances.

    --headless matters: without it the client starts a TUI and spends a
    second waiting for replies from the terminal before it says anything.
    """
    runtime_dir = Path(
        os.environ.get("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}")
    )
    for socket in sorted(runtime_dir.glob("nvim.*")):
        run(
            [
                "nvim",
                "--headless",
                "--server",
                str(socket),
                "--remote-expr",
                f"execute('set background={theme}')",
            ],
            stdout=DEVNULL,
            stderr=DEVNULL,
            timeout=5,
            check=False,
        )


def update_running_zsh(theme: str) -> None:
    """Repaint running shells.

    .zshrc rebuilds its prompt and the colors it hands to git and fzf when it
    gets a SIGWINCH. Older shells that don't know about this simply redraw,
    which is why this is WINCH and not USR1.
    """
    run(
        ["pkill", "-WINCH", "-x", "-u", str(os.getuid()), "zsh"],
        stdout=DEVNULL,
        stderr=DEVNULL,
        timeout=5,
        check=False,
    )


def update_running_tmux(theme: str) -> None:
    """Restyle running tmux servers."""
    run(
        [
            "tmux",
            "source-file",
            str(HOME_DIR / f".config/theme.d/{theme}.colors.conf"),
        ],
        stdout=DEVNULL,
        stderr=DEVNULL,
        timeout=5,
        check=False,
    )


def update_gtk2_config(theme: str) -> None:
    config_path = HOME_DIR / ".gtkrc-2.0"
    if config_path.exists():
        config = config_path.read_text()
    else:
        config = ""
    gtk_theme = "Arc-Dark" if theme == "dark" else "Arc"
    lines = config.splitlines()
    lines = [line for line in lines if not line.startswith("gtk-theme-name")]
    lines.append(f'gtk-theme-name="{gtk_theme}"')
    config = "\n".join(lines) + "\n"
    config_path.write_text(config)


def update_gtk3_config(theme: str) -> None:
    config_path = HOME_DIR / ".config" / "gtk-3.0" / "settings.ini"
    if config_path.exists():
        config = config_path.read_text()
    else:
        config = "[Settings]"
    gtk_theme = "Arc-Dark" if theme == "dark" else "Arc"
    lines = config.splitlines()
    lines = [line for line in lines if not line.startswith("gtk-theme-name")]
    lines.append(f'gtk-theme-name="{gtk_theme}"')
    config = "\n".join(lines) + "\n"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(config)

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
    args = parse_args()
    if args.theme is None:
        print(current_theme("unknown"))
        return
    for func in [
        update_generated_colors,
        update_wezterm_config,
        update_theme_marker,
        update_running_nvim,
        update_running_tmux,
        update_running_zsh,
        update_gtk2_config,
        update_gtk3_config,
    ]:
        func(args.theme)


if __name__ == "__main__":
    main()
