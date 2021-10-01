import os

from libdotfiles import packages, util


def run() -> None:
    packages.try_install("libxkbcommon-x11")
    packages.try_install("python-pyqt5")
    packages.try_install("qt5-svg")

    util.copy_file("./start", "~/.config/x/start-panel.sh")

    os.chdir(util.REPO_ROOT_DIR / "opt" / "panel")
    util.run_verbose(
        ["python3", "-m", "pip", "install", "--user", "--editable", "."]
    )
