from libdotfiles.util import HOME_DIR, PKG_DIR, create_symlink

create_symlink(PKG_DIR / "backup.yml", HOME_DIR / ".config" / "backup.yml")
