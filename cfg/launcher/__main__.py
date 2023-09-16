import os

from libdotfiles.util import (
    HOME_DIR,
    PKG_DIR,
    REPO_ROOT_DIR,
    create_symlink,
    run,
)

create_symlink(
    PKG_DIR / "launcher.json", HOME_DIR / ".config" / "launcher.json"
)

os.chdir(REPO_ROOT_DIR / "opt" / "launcher")
run(
    [
        "python3",
        "-m",
        "pip",
        "install",
        "--user",
        "--upgrade",
        "--break-system-packages",
        ".",
    ],
    check=False,
)
