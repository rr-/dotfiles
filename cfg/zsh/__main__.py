from libdotfiles.packages import try_install
from libdotfiles.util import (
    HOME_DIR,
    PKG_DIR,
    create_dir,
    create_symlinks,
    run,
)

try_install("zsh")

create_symlinks(
    [
        (PKG_DIR / "zshrc", HOME_DIR / ".zshrc"),
        (PKG_DIR / "zprofile", HOME_DIR / ".zprofile"),
        (PKG_DIR / "zshenv", HOME_DIR / ".zshenv"),
    ]
)

create_dir(HOME_DIR / ".config" / "zsh")
run(
    ["lesskey", "-o", HOME_DIR / ".less", "--", PKG_DIR / "lesskey"],
    check=False,
)