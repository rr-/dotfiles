from libdotfiles.packages import try_install
from libdotfiles.util import HOME_DIR, PKG_DIR, create_symlinks

try_install("git")
try_install("git-extras")

# to generate a new key: gpg --full-generate-key

create_symlinks(
    [
        (PKG_DIR / "config", HOME_DIR / ".config" / "git"),
        (PKG_DIR / "config" / "ignore", HOME_DIR / ".gitignore"),
    ]
)
