import os

from dotinstall import packages, util


def run():
    util.create_symlink("~/data/text/pw.dat", "~/.config/")
    os.chdir(util.root_dir / "opt" / "pw")
    util.run_verbose(["pip", "install", "--user", "--editable", "."])
