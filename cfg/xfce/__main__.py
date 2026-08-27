import re
from subprocess import DEVNULL, PIPE, run

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


# How much of the desktop a maximized window leaves alone. Nothing: a
# maximized window meets the screen's edges and the panel, and its own border
# is the only thing between them and what it is showing.
#
# Written rather than left out, so that a value set by hand once is cleared
# rather than kept. Floating windows are not covered either way: a margin is
# a strut, and only maximizing reads it.
GAP = 0

# What the glass bezel needs that is not per-switch. The frames themselves are
# drawn by cfg/theme/xfwm.py and picked by cfg/theme/switch.py.
for channel, prop, value in [
    ("xfwm4", "/general/margin_top", "0"),
    ("xfwm4", "/general/margin_bottom", str(GAP)),
    ("xfwm4", "/general/margin_left", str(GAP)),
    ("xfwm4", "/general/margin_right", str(GAP)),
    # picom composites instead: xfwm4's compositor cannot blur
    ("xfwm4", "/general/use_compositing", "false"),
    # a shadow over a translucent border reads as the border
    ("xfwm4", "/general/show_frame_shadow", "false"),
    ("xfwm4", "/general/show_dock_shadow", "false"),
    # a maximized window cannot be resized, so xfwm4 drops the borders it
    # resizes by and leaves the title row alone: three sides of the bezel
    # gone on the windows most likely to be looked at
    ("xfwm4", "/general/borderless_maximize", "false"),
    # xfwm4 antialiases the title, and an antialiased edge is partial
    # alpha, which it punches through the frame as a cutout. Drawing the
    # text in the film hides the solid pixels; shrinking the font is what
    # deals with the fringe left over, which fell across the rules
    ("xfwm4", "/general/title_font", "Sans 1"),
    # nothing on the title: no buttons, and the text is drawn in the film
    ("xfwm4", "/general/button_layout", "|"),
]:
    run(
        ["xfconf-query", "-c", channel, "-p", prop, "-s", value],
        stdout=DEVNULL,
        stderr=DEVNULL,
        check=False,
    )


# The panel's layout lives in xfconf, not in this repo: it is whatever the
# desktop was last dragged into. Only the weather plugin is claimed here, and
# only when the panel does not already carry one, so a re-run never stacks a
# second copy.
#
# The plugin list is not ours to edit directly. A running xfce4-panel holds
# its layout in memory and writes the whole thing back over xfconf, so an
# xfconf-side insert is either clobbered or duplicated depending on the
# timing. --add hands the request to the panel that owns the list.


def has_weather_plugin() -> bool:
    listing = run(
        ["xfconf-query", "-c", "xfce4-panel", "-p", "/plugins", "-l", "-v"],
        stdout=PIPE,
        stderr=DEVNULL,
        text=True,
        check=False,
    ).stdout
    # the listing carries each plugin's own settings too; only the bare
    # /plugins/plugin-N rows name a plugin type
    return any(
        re.fullmatch(r"/plugins/plugin-\d+\s+weather", line.strip())
        for line in listing.splitlines()
    )


if try_install("xfce4-weather-plugin") and not has_weather_plugin():
    # only a running panel can be added to; on a fresh machine this is a
    # no-op and the next run of this package picks it up
    run(["xfce4-panel", "--add=weather"], stderr=DEVNULL, check=False)
    # the plugin has no location until one is picked in its properties
    # dialog, which is where it writes ~/.config/xfce4/panel/weather-N.rc
