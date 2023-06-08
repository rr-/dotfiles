from libdotfiles.packages import try_install
from libdotfiles.util import HOME_DIR, PKG_DIR, create_symlink

try_install("syncthing")
create_symlink(
    PKG_DIR / "syncthing.service",
    HOME_DIR / ".config/systemd/user/syncthing.service",
)
