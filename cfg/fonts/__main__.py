from pathlib import Path

from libdotfiles.packages import try_install
from libdotfiles.util import (
    HOME_DIR,
    PKG_DIR,
    create_dir,
    create_symlink,
    create_symlinks,
    distro_name,
    has_executable,
    run,
)

if distro_name() == "arch":
    try_install("ttf-dejavu")
    try_install("ttf-ms-fonts")
    try_install("ttf-ipa-mona")
    try_install("adobe-source-han-sans-otc-fonts")
    try_install("adobe-source-han-serif-otc-fonts")
else:
    try_install("xfonts-utils")
    try_install("fonts-ipafont")
    try_install("fonts-dejavu")
    try_install("fonts-symbola")
    try_install("fonts-font-awesome")
    try_install("fonts-monapo")

if Path("/usr/share/fonts").exists():
    fonts_dir = HOME_DIR / ".local" / "share" / "fonts"

    create_dir(fonts_dir)
    create_symlinks(
        [
            (font_path, fonts_dir / font_path.name)
            for font_path in PKG_DIR.glob("*.ttf")
        ]
    )

    if has_executable("mkfontscale"):
        run(["mkfontscale", fonts_dir], check=False)
    if has_executable("mkfontdir"):
        run(["mkfontdir", fonts_dir], check=False)
    if has_executable("xset"):
        run(["xset", "+fp", fonts_dir], check=False)
        run(["xset", "fp", "rehash"], check=False)

if has_executable("fc-cache"):
    create_symlink(
        PKG_DIR / "fonts.conf",
        HOME_DIR / ".config" / "fontconfig" / "fonts.conf",
    )
    run(["fc-cache"], check=False)

if Path("/etc/fonts/conf.d/50-user.conf").exists():
    run(
        [
            "sudo",
            "mv",
            "/etc/fonts/conf.d/50-user.conf",
            "/etc/fonts/conf.d/99-user.conf",
        ],
        check=True,
    )
