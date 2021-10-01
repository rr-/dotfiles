from .logging import setup_colored_logs
from .util import HOME_DIR, LIBDOTFILES_DIR, PKG_DIR, REPO_ROOT_DIR

setup_colored_logs()

__all__ = [
    "HOME_DIR",
    "LIBDOTFILES_DIR",
    "PKG_DIR",
    "REPO_ROOT_DIR",
]
