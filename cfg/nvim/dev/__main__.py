from libdotfiles.packages import try_install
from libdotfiles.util import (
    HOME_DIR,
    PKG_DIR,
    create_symlinks,
    get_distro_name,
    run,
)

NVIM_DIR = HOME_DIR / ".config" / "nvim"

if get_distro_name() == "linuxmint":
    try_install("python3-neovim")
else:
    try_install("pynvim", method="pip")
try_install("ruff", method="pip")
try_install("ty", method="pip")

create_symlinks(
    [
        (PKG_DIR / name, NVIM_DIR / name)
        for name in ["plugins.vim", "nvim-pack-lock.json"]
    ]
)

run(["nvim", "--headless", "-c", "qa"], check=False)
