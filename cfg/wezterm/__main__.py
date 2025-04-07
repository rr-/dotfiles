from libdotfiles.packages import try_install
from libdotfiles.util import HOME_DIR, PKG_DIR, copy_file, create_symlink

cfg_dir = HOME_DIR / ".config" / "wezterm"

try_install("wezterm")
create_symlink(PKG_DIR / "wezterm.lua", cfg_dir / "wezterm.lua")
create_symlink(PKG_DIR / "stardust-dark.lua", cfg_dir / "stardust-dark.lua")
create_symlink(PKG_DIR / "stardust-light.lua", cfg_dir / "stardust-light.lua")
copy_file(PKG_DIR / "runtime.lua", cfg_dir / "runtime.lua")
create_symlink(PKG_DIR / "colors", cfg_dir / "colors")
