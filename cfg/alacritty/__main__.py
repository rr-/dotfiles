from libdotfiles.packages import try_install
from libdotfiles.util import HOME_DIR, PKG_DIR, create_symlink

try_install("alacritty")
create_symlink(
    PKG_DIR / "alacritty.toml",
    HOME_DIR / ".config" / "alacritty" / "alacritty.base.toml",
)
create_symlink(
    PKG_DIR / "alacritty.light.toml",
    HOME_DIR / ".config" / "alacritty" / "alacritty.light.toml",
)
create_symlink(
    PKG_DIR / "alacritty.dark.toml",
    HOME_DIR / ".config" / "alacritty" / "alacritty.dark.toml",
)
