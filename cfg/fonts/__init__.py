import os

from libdotfiles import packages, util


def run() -> None:
    packages.try_install("xfonts-utils")
    packages.try_install("fonts-ipafont")
    packages.try_install("fonts-dejavu")
    packages.try_install("fonts-symbola")
    packages.try_install("fonts-font-awesome")
    packages.try_install("fonts-monapo")

    if os.path.exists("/usr/share/fonts"):
        fonts_dir = "~/.local/share/fonts/"

        util.create_dir(fonts_dir)
        for font_path in util.find("./*.ttf"):
            util.create_symlink(font_path, fonts_dir)

        if util.has_executable("mkfontscale"):
            util.run_verbose(["mkfontscale", util.expand_path(fonts_dir)])
        if util.has_executable("mkfontdir"):
            util.run_verbose(["mkfontdir", util.expand_path(fonts_dir)])
        if util.has_executable("xset"):
            util.run_verbose(["xset", "+fp", util.expand_path(fonts_dir)])
            util.run_verbose(["xset", "fp", "rehash"])

    if util.has_executable("fc-cache"):
        util.create_symlink("./fonts.conf", "~/.config/fontconfig/")
        util.run_verbose(["fc-cache"])
