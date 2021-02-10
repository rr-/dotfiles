import os

from libdotfiles import packages, util


def run():
    util.create_symlink("./launcher.json", "~/.config/launcher.json")
    os.chdir(util.REPO_ROOT_DIR / "opt" / "launcher")
    util.run_verbose(
        [packages.PIP_EXECUTABLE, "install", "--user", "--upgrade", "."]
    )
