from libdotfiles.packages import try_install
from libdotfiles.util import HOME_DIR, PKG_DIR, create_symlink, run

try_install("tmux")
create_symlink(PKG_DIR / "tmux.conf", HOME_DIR / ".tmux.conf")
create_symlink(PKG_DIR / "config", HOME_DIR / ".config" / "tmux")
run(
    [
        "git",
        "clone",
        "https://github.com/tmux-plugins/tpm",
        HOME_DIR / ".config" / "tmux" / "plugins" / "tpm",
    ],
    check=True,
)
