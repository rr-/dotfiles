from libdotfiles.packages import try_install
from libdotfiles.util import HOME_DIR, PKG_DIR, create_symlinks

try_install("bspwm")
try_install("dmenu")  # program executor
try_install("feh")  # wallpaper renderer
try_install("i3lock")  # lock screen

create_symlinks(
    [
        (PKG_DIR / "bspwmrc", HOME_DIR / ".config" / "bspwm" / "bspwmrc"),
        (PKG_DIR / "rules", HOME_DIR / ".config" / "bspwm" / "rules"),
        (PKG_DIR / "start", HOME_DIR / ".config" / "x" / "start-wm.sh"),
    ]
)
