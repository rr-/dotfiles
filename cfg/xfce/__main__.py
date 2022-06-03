from libdotfiles.packages import try_install
from libdotfiles.util import HOME_DIR, PKG_DIR, create_symlinks

try_install("xfce4")

create_symlinks(
    [
        (PKG_DIR / "start", HOME_DIR / ".config" / "x" / "start-wm.sh"),
        (PKG_DIR / "sxhkdrc", HOME_DIR / ".config" / "sxhkd" / "xfce.sxhkdrc"),
    ]
)
