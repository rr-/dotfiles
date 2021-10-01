from libdotfiles import packages, util


def run() -> None:
    packages.try_install("git")
    packages.try_install("git-extras-git")
    util.create_symlink("./config", "~/.config/git")
    util.create_symlink("./config/ignore", "~/.gitignore")
