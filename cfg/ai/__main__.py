from libdotfiles.util import HOME_DIR, PKG_DIR, create_dir, create_symlink

AI_DIR = HOME_DIR / ".config" / "ai"

create_dir(AI_DIR)
create_symlink(PKG_DIR / "commands", AI_DIR / "commands")
