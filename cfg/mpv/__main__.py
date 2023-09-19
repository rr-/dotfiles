from libdotfiles.packages import try_install
from libdotfiles.util import HOME_DIR, PKG_DIR, create_symlink, get_distro_name

if get_distro_name() == "arch":
    try_install("mujs")
    try_install("luajit")

try_install("mpv")
create_symlink(PKG_DIR / "config", HOME_DIR / ".config" / "mpv")
