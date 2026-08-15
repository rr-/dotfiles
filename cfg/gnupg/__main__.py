from libdotfiles.packages import try_install
from libdotfiles.util import HOME_DIR, PKG_DIR, create_dir, create_symlink, run

try_install("gnupg")

gnupg_dir = HOME_DIR / ".gnupg"
create_dir(gnupg_dir)
# gpg refuses to use a home directory others can read
gnupg_dir.chmod(0o700)

create_symlink(PKG_DIR / "gpg-agent.conf", gnupg_dir / "gpg-agent.conf")

# pick up the new cache TTLs without waiting for a logout
run(["gpg-connect-agent", "reloadagent", "/bye"], check=False)
