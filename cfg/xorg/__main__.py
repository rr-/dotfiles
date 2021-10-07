from libdotfiles.packages import try_install
from libdotfiles.util import HOME_DIR, PKG_DIR, create_symlinks

try_install("xorg")  # the server itself
try_install("xclip")  # for clip to work
try_install("xorg-xinit")  # for startx
try_install("xorg-xsetroot")  # to fix the mouse cursor
try_install("xorg-xrandr")  # to query monitor information
try_install("xdotool")  # for all sort of things
try_install("autocutsel")  # sync primary and selection clipboards
try_install("clipit")  # keep clipboard data after process exit
try_install("pkg-config")  # for picom
try_install("picom")  # for shadows, transparency and vsync
try_install("xdg", method="pip")  # for XDG_CONFIG_HOME

create_symlinks(
    [
        (PKG_DIR / "xinitrc", HOME_DIR / ".xinitrc"),
        (PKG_DIR / "picom.conf", HOME_DIR / ".config" / "picom.conf"),
        (PKG_DIR / "picom.conf", HOME_DIR / ".config" / "compton.conf"),
    ]
)
