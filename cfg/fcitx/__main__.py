from libdotfiles import HOME_DIR, PKG_DIR
from libdotfiles.packages import try_install
from libdotfiles.util import create_symlink

try_install("fcitx5")
try_install("fcitx5-anthy")
try_install("fcitx5-configtool")
try_install("fcitx5-qt5")
try_install("fcitx5-gtk")

create_symlink(
    PKG_DIR / "start", HOME_DIR / ".config" / "x" / "start-fcitx.sh"
)
create_symlink(
    PKG_DIR / "zsh_config", HOME_DIR / ".config" / "zsh" / "fcitx.sh"
)
