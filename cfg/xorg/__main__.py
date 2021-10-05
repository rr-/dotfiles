from libdotfiles import HOME_DIR, PKG_DIR, packages, util

packages.try_install("xorg")  # the server itself
packages.try_install("xclip")  # for clip to work
packages.try_install("xorg-xinit")  # for startx
packages.try_install("xorg-xsetroot")  # to fix the mouse cursor
packages.try_install("xorg-xrandr")  # to query monitor information
packages.try_install("xdotool")  # for all sort of things
packages.try_install("autocutsel")  # sync primary and selection clipboards
packages.try_install("clipit")  # keep clipboard data after process exit
packages.try_install("pkg-config")  # for compton
packages.try_install("compton")  # for shadows, transparency and vsync
packages.try_install("shot-git")  # for screenshots
packages.try_install("xdg", method="pip")  # for XDG_CONFIG_HOME

util.create_symlinks(
    [
        (PKG_DIR / "xinitrc", HOME_DIR / ".xinitrc"),
        (PKG_DIR / "compton.conf", HOME_DIR / ".config" / "compton.conf"),
    ]
)
