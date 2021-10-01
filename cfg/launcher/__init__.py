import os

from libdotfiles import packages, util


def run() -> None:
    util.create_symlink("./launcher.json", "~/.config/launcher.json")
    os.chdir(util.REPO_ROOT_DIR / "opt" / "launcher")
    util.run_verbose(
        ["python3", "-m", "pip", "install", "--user", "--upgrade", "."]
    )
