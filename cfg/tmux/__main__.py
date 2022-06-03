from libdotfiles.packages import try_install
from libdotfiles.util import HOME_DIR, PKG_DIR, create_symlink, git_clone

try_install("tmux")
create_symlink(PKG_DIR / "tmux.conf", HOME_DIR / ".tmux.conf")
create_symlink(PKG_DIR / "config", HOME_DIR / ".config" / "tmux")

git_clone(
    "https://github.com/tmux-plugins/tpm",
    HOME_DIR / ".config" / "tmux" / "plugins" / "tpm",
)
