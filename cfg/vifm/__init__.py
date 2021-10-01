from libdotfiles import packages, util


def run() -> None:
    if not util.has_executable("vifm"):
        packages.try_install("vifm")
    util.create_dir("~/.config/vifm")
    util.create_symlink("./vifmrc", "~/.config/vifm/vifmrc")
    util.create_symlink("./colors", "~/.config/vifm/colors")
