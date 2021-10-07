from libdotfiles.packages import try_install
from libdotfiles.util import (
    HOME_DIR,
    PKG_DIR,
    create_dir,
    create_symlinks,
    has_executable,
)

if not has_executable("vifm"):
    try_install("vifm")

create_dir(HOME_DIR / ".config" / "vifm")
create_symlinks(
    [
        (PKG_DIR / "vifmrc", HOME_DIR / ".config" / "vifm" / "vifmrc"),
        (PKG_DIR / "colors", HOME_DIR / ".config" / "vifm" / "colors"),
    ]
)
