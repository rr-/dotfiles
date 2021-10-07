from libdotfiles.packages import try_install
from libdotfiles.util import HOME_DIR, PKG_DIR, create_symlink

try_install("signal-desktop")

create_symlink(
    PKG_DIR / "start", HOME_DIR / ".config" / "x" / "start-signal.sh"
)
