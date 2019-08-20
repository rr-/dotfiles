import os

from dotinstall import packages, util


def run():
    packages.try_install("libxkbcommon-x11")
    packages.try_install("python-pyqt5")
    packages.try_install("qt5-svg")

    util.copy_file("./start", "~/.config/x/start-panel.sh")

    os.chdir(util.root_dir / "opt" / "panel")
    util.run_verbose(["pip", "install", "--user", "--editable", "."])
