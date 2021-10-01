import os
import tempfile

from libdotfiles import packages, util

if util.distro_name() == "arch":
    packages.try_install("translate-shell-git")
elif util.distro_name() == "linuxmint":
    with tempfile.TemporaryDirectory() as tmp_dir:
        os.chdir(tmp_dir)
        util.run_verbose(
            ["git", "clone", "https://github.com/soimort/translate-shell"]
        )
        os.chdir("translate-shell")
        util.run_verbose(["make"])
        util.run_verbose(["sudo", "make", "install"])
