from libdotfiles.packages import try_install
from libdotfiles.util import HOME_DIR, PKG_DIR, create_dir, create_symlink

try_install("github-cli")

# hosts.yml, which holds the token, comes from the secrets repository
create_dir(HOME_DIR / ".config" / "gh")
create_symlink(
    PKG_DIR / "config.yml", HOME_DIR / ".config" / "gh" / "config.yml"
)
