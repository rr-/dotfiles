from libdotfiles import packages, util


def run() -> None:
    packages.try_install("urxvt-perls")
    packages.try_install("rxvt-unicode")

    util.create_symlink("./ext", "~/.urxvt/ext")
    util.create_symlink("./Xresources", "~/.config/Xresources")
    util.create_symlink("./notify-urxvt", "~/.local/bin/")

    if util.exists("/usr/lib/urxvt/perl/keyboard-select") and not util.exists(
        "/usr/local/lib/urxvt/perl/keyboard-select"
    ):
        util.create_symlink(
            "/usr/lib/urxvt/perl/keyboard-select",
            "/usr/local/lib/urxvt/perl/keyboard-select",
        )
