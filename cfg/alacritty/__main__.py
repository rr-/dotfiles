from libdotfiles.packages import try_install
from libdotfiles.util import HOME_DIR, PKG_DIR, copy_file

try_install("alacritty")
copy_file(
    PKG_DIR / "alacritty.yml",
    HOME_DIR / ".config" / "alacritty" / "alacritty.yml",
)
