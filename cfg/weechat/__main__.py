from libdotfiles.packages import try_install
from libdotfiles.util import HOME_DIR, PKG_DIR, create_symlinks

try_install("weechat")
create_symlinks(
    [
        (path, HOME_DIR / ".weechat" / path.name)
        for path in PKG_DIR.glob("*.conf")
    ]
)
create_symlinks(
    [
        (path, HOME_DIR / ".weechat" / "python" / path.name)
        for path in (PKG_DIR / "python").glob("*.conf")
    ]
)
