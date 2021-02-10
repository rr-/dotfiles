import os

from libdotfiles import packages, util


def run():
    packages.install("base-devel", method="pacman")
    packages.install("expac", method="pacman")
    packages.install("meson", method="pacman")
    packages.install("gtest", method="pacman")
    packages.install("gmock", method="pacman")
    packages.install("jq", method="pacman")
    packages.install("sudo", method="pacman")

    os.chdir("/tmp")
    util.run_verbose(
        ["git", "clone", "https://aur.archlinux.org/auracle-git.git"]
    )
    os.chdir("/tmp/auracle-git")
    util.run_verbose(["makepkg", "-i", "--skippgpcheck"])

    os.chdir("/tmp")
    util.run_verbose(["git", "clone", "https://aur.archlinux.org/pacaur.git"])
    os.chdir("/tmp/pacaur")
    util.run_verbose(["makepkg", "-i", "--skippgpcheck"])
