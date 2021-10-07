import os
import tempfile

from libdotfiles.packages import try_install
from libdotfiles.util import distro_name, run

if distro_name() == "arch":
    try_install("base-devel")
    try_install("expac")
    try_install("fakechroot")
    try_install("fakeroot")
    try_install("gtest")
    try_install("jq")
    try_install("meson")
    try_install("sudo")

    with tempfile.TemporaryDirectory() as tmp_dir:
        os.chdir(tmp_dir)
        run(
            ["git", "clone", "https://aur.archlinux.org/auracle-git.git"],
            check=True,
        )
        os.chdir(os.path.join(tmp_dir, "auracle-git"))
        run(["makepkg", "-i", "--skippgpcheck"], check=True)

    with tempfile.TemporaryDirectory() as tmp_dir:
        os.chdir(tmp_dir)
        run(
            ["git", "clone", "https://aur.archlinux.org/pacaur.git"],
            check=True,
        )
        os.chdir(os.path.join(tmp_dir, "pacaur"))
        run(["makepkg", "-i", "--skippgpcheck"], check=True)
