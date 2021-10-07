import os
import tempfile

from libdotfiles.packages import try_install
from libdotfiles.util import distro_name, run

if distro_name() == "arch":
    try_install("translate-shell-git")
elif distro_name() == "linuxmint":
    with tempfile.TemporaryDirectory() as tmp_dir:
        os.chdir(tmp_dir)
        run(
            ["git", "clone", "https://github.com/soimort/translate-shell"],
            check=True,
        )
        os.chdir("translate-shell")
        run(["make"], check=True)
        run(["sudo", "make", "install"], check=True)
