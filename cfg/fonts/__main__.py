from pathlib import Path

from libdotfiles import HOME_DIR, PKG_DIR, packages, util

if util.distro_name() == "arch":
    # packages.try_install("xfonts-utils")
    # packages.try_install("otf-ipafont")
    packages.try_install("ttf-dejavu")
    # packages.try_install("ttf-symbola")
    # packages.try_install("ttf-font-awesome")
    # packages.try_install("otf-monapo")
else:
    packages.try_install("xfonts-utils")
    packages.try_install("fonts-ipafont")
    packages.try_install("fonts-dejavu")
    packages.try_install("fonts-symbola")
    packages.try_install("fonts-font-awesome")
    packages.try_install("fonts-monapo")

if Path("/usr/share/fonts").exists():
    fonts_dir = HOME_DIR / ".local" / "share" / "fonts"

    util.create_dir(fonts_dir)
    util.create_symlinks(
        [
            (font_path, fonts_dir / font_path.name)
            for font_path in PKG_DIR.glob("*.ttf")
        ]
    )

    if util.has_executable("mkfontscale"):
        util.run_verbose(["mkfontscale", fonts_dir])
    if util.has_executable("mkfontdir"):
        util.run_verbose(["mkfontdir", fonts_dir])
    if util.has_executable("xset"):
        util.run_verbose(["xset", "+fp", fonts_dir])
        util.run_verbose(["xset", "fp", "rehash"])

if util.has_executable("fc-cache"):
    util.create_symlink(
        PKG_DIR / "fonts.conf",
        HOME_DIR / ".config" / "fontconfig" / "fonts.conf",
    )
    util.run_verbose(["fc-cache"])
