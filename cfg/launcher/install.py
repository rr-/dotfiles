import os

from dotinstall import util


def run():
    util.create_symlink("./launcher.json", "~/.config/launcher.json")
    os.chdir(util.root_dir / "opt" / "launcher")
    util.run_verbose(["pip", "install", "--user", "--upgrade", "."])
