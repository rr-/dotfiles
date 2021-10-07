from libdotfiles.packages import try_install
from libdotfiles.util import HOME_DIR, PKG_DIR, create_symlink

try_install("htop")
create_symlink(PKG_DIR / "htoprc", HOME_DIR / ".config" / "htop" / "htoprc")
