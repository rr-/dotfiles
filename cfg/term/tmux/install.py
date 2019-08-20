from os.path import expanduser

from dotinstall import packages, util


def run():
    packages.try_install("tmux")
    util.create_symlink("./tmux.conf", "~/.tmux.conf")
    util.create_symlink("./config", "~/.config/tmux")
    util.run_verbose(
        [
            "git",
            "clone",
            "https://github.com/tmux-plugins/tpm",
            expanduser("~/.config/tmux/plugins/tpm"),
        ]
    )
