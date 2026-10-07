from libdotfiles.packages import try_install
from libdotfiles.util import (
    HOME_DIR,
    PKG_DIR,
    create_symlinks,
    get_distro_name,
)

try_install("git")
try_install("git-extras")
if get_distro_name() == "arch":
    try_install("github-cli")
else:
    try_install("gh", method="apt")

# to generate a new key: gpg --full-generate-key

create_symlinks(
    [
        (PKG_DIR / "config", HOME_DIR / ".config" / "git"),
        (PKG_DIR / "config" / "ignore", HOME_DIR / ".gitignore"),
    ]
)
