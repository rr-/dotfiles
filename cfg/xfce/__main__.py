from subprocess import DEVNULL, run

from libdotfiles.packages import try_install
from libdotfiles.util import HOME_DIR, PKG_DIR, create_symlinks

try_install("xfce4")

create_symlinks(
    [
        (PKG_DIR / "start", HOME_DIR / ".config" / "x" / "start-wm.sh"),
        (PKG_DIR / "sxhkdrc", HOME_DIR / ".config" / "sxhkd" / "xfce.sxhkdrc"),
        (PKG_DIR / "picom.conf", HOME_DIR / ".config" / "picom-xfce.conf"),
    ]
)


# What the glass bezel needs that is not per-switch. The frames themselves are
# drawn by cfg/theme/xfwm.py and picked by cfg/theme/switch.py.
for channel, prop, value in [
    # picom composites instead: xfwm4's compositor cannot blur
    ("xfwm4", "/general/use_compositing", "false"),
    # a shadow over a translucent border reads as the border
    ("xfwm4", "/general/show_frame_shadow", "false"),
    ("xfwm4", "/general/show_dock_shadow", "false"),
    # nothing on the title: no buttons, and the text is drawn in the film
    ("xfwm4", "/general/button_layout", "|"),
]:
    run(
        ["xfconf-query", "-c", channel, "-p", prop, "-s", value],
        stdout=DEVNULL,
        stderr=DEVNULL,
        check=False,
    )
