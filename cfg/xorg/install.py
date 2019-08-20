from dotinstall import packages, util


def run():
    # the server itself
    packages.try_install("xorg")
    # for clip to work
    packages.try_install("xclip")
    # for startx
    packages.try_install("xorg-xinit")
    # to fix the mouse cursor
    packages.try_install("xorg-xsetroot")
    # to query monitor information
    packages.try_install("xorg-xrandr")
    # for all sort of things
    packages.try_install("xdotool")
    # sync primary and selection clipboards
    packages.try_install("autocutsel")
    # keep clipboard data after process exit
    packages.try_install("clipit")
    # for compton
    packages.try_install("pkg-config")
    # for shadows, transparency and vsync
    packages.try_install("compton")
    # for screenshots
    packages.try_install("shot-git")

    util.create_symlink("./xinitrc", "~/.xinitrc")
    util.create_symlink("./compton.conf", "~/.config/compton.conf")
