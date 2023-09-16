from libdotfiles.packages import try_install
from libdotfiles.util import HOME_DIR, PKG_DIR, create_symlinks

try_install("fcitx5")
try_install("fcitx5-anthy")
try_install("fcitx5-configtool")
try_install("fcitx5-qt")
try_install("fcitx5-gtk")

create_symlinks(
    [
        (PKG_DIR / "start", HOME_DIR / ".config" / "x" / "start-fcitx.sh"),
        (PKG_DIR / "zsh_config", HOME_DIR / ".config" / "zsh" / "fcitx.sh"),
    ]
)
