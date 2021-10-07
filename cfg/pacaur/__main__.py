import os
import tempfile

from libdotfiles import packages, util

if util.distro_name() == "arch":
    packages.try_install("base-devel")
    packages.try_install("expac")
    packages.try_install("fakechroot")
    packages.try_install("fakeroot")
    packages.try_install("gtest")
    packages.try_install("jq")
    packages.try_install("meson")
    packages.try_install("sudo")

    with tempfile.TemporaryDirectory() as tmp_dir:
        os.chdir(tmp_dir)
        util.run_verbose(
            ["git", "clone", "https://aur.archlinux.org/auracle-git.git"]
        )
        os.chdir(os.path.join(tmp_dir, "auracle-git"))
        util.run_verbose(["makepkg", "-i", "--skippgpcheck"])

    with tempfile.TemporaryDirectory() as tmp_dir:
        os.chdir(tmp_dir)
        util.run_verbose(
            ["git", "clone", "https://aur.archlinux.org/pacaur.git"]
        )
        os.chdir(os.path.join(tmp_dir, "pacaur"))
        util.run_verbose(["makepkg", "-i", "--skippgpcheck"])
