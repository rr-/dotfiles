from libdotfiles.util import HOME_DIR, PKG_DIR, create_symlink

create_symlink(
    PKG_DIR / "start", HOME_DIR / ".config" / "x" / "start-powercap.sh"
)
