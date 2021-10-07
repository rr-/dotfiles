from libdotfiles.packages import try_install
from libdotfiles.util import HOME_DIR, PKG_DIR, create_symlinks, has_executable

if not has_executable("mpv"):
    try_install("luajit")
    try_install("mpv")

create_symlinks(
    [
        (PKG_DIR / "config", HOME_DIR / ".config" / "mpi"),
        (PKG_DIR / "mpi", HOME_DIR / ".local" / "bin" / "mpi"),
    ]
)
