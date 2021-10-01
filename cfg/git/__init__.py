from libdotfiles import packages, util


def run() -> None:
    packages.try_install("git")
    packages.try_install("git-extras-git")
    util.create_symlink("./gitconfig", "~/.config/git/config")
    util.create_symlink("./gitconfig-moto", "~/.config/git/config-moto")
    util.create_symlink("./gitconfig-priv", "~/.config/git/config-priv")
    util.create_symlink("./gitignore", "~/.config/git/ignore")
