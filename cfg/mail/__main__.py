from libdotfiles.packages import try_install
from libdotfiles.util import (
    HOME_DIR,
    PKG_DIR,
    create_dir,
    create_file,
    create_symlinks,
)

try_install("getmail")
create_dir(HOME_DIR / "mail" / "new")
create_dir(HOME_DIR / "mail" / "cur")
create_dir(HOME_DIR / "mail" / "tmp")

try_install("neomutt")
try_install("w3m")
try_install("lynx")
try_install("docbook-xsl")
create_file(HOME_DIR / ".mutt" / "certificates")
create_dir(HOME_DIR / ".mutt" / "cache" / "bodies")
create_dir(HOME_DIR / ".mutt" / "cache" / "headers")

create_symlinks(
    [
        (PKG_DIR / filename, HOME_DIR / ".mutt" / filename)
        for filename in ["file_email", "colors.muttrc", "muttrc", "mailcap"]
    ]
)
