from libdotfiles import HOME_DIR, PKG_DIR, packages, util

packages.try_install("bspwm")
packages.try_install("dmenu")  # program executor
packages.try_install("feh")  # wallpaper renderer
packages.try_install("i3lock")  # lock screen

util.create_symlink(
    PKG_DIR / "bspwmrc", HOME_DIR / ".config" / "bspwm" / "bspwmrc"
)
util.create_symlink(
    PKG_DIR / "rules", HOME_DIR / ".config" / "bspwm" / "rules"
)
util.create_symlink(
    PKG_DIR / "start", HOME_DIR / ".config" / "x" / "start-wm.sh"
)
