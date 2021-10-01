import os

from libdotfiles import HOME_DIR, PKG_DIR, REPO_ROOT_DIR, packages, util

util.create_symlink(
    PKG_DIR / "launcher.json", HOME_DIR / ".config" / "launcher.json"
)

os.chdir(REPO_ROOT_DIR / "opt" / "launcher")
util.run_verbose(
    ["python3", "-m", "pip", "install", "--user", "--upgrade", "."]
)
