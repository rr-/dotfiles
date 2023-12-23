import os

from libdotfiles.packages import try_install
from libdotfiles.util import REPO_ROOT_DIR, run

try_install("xdg", method="pip")  # for XDG_CONFIG_HOME

os.chdir(REPO_ROOT_DIR / "opt" / "authenticator")
run(
    [
        "python3",
        "-m",
        "pip",
        "install",
        "--user",
        "--break-system-packages",
        "--editable",
        ".",
    ],
    check=False,
)
