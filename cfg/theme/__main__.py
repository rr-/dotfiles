from cfg.theme.render import current_theme
from libdotfiles.packages import try_install
from libdotfiles.util import HOME_DIR, create_script, get_distro_name, run

# cfg/theme/xfwm.py draws the window frames with it
if get_distro_name() == "arch":
    try_install("python-pillow")
else:
    try_install("pillow", method="pip")

create_script("cfg.theme.switch", "theme")
# a machine where theme(1) has never run has nothing for zsh and tmux to
# source, so put it on a theme now rather than at the first switch
run([HOME_DIR / ".local" / "bin" / "theme", current_theme("dark")], check=True)
