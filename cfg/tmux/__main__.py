from libdotfiles import HOME_DIR, PKG_DIR, packages, util

packages.try_install("tmux")
util.create_symlink(PKG_DIR / "tmux.conf", HOME_DIR / ".tmux.conf")
util.create_symlink(PKG_DIR / "config", HOME_DIR / ".config" / "tmux")
util.run_verbose(
    [
        "git",
        "clone",
        "https://github.com/tmux-plugins/tpm",
        HOME_DIR / ".config" / "tmux" / "plugins" / "tpm",
    ]
)
