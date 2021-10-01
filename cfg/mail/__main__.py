from libdotfiles import HOME_DIR, PKG_DIR, packages, util

packages.try_install("getmail")
util.create_dir(HOME_DIR / "mail" / "new")
util.create_dir(HOME_DIR / "mail" / "cur")
util.create_dir(HOME_DIR / "mail" / "tmp")

packages.try_install("neomutt")
packages.try_install("w3m")
packages.try_install("lynx")
packages.try_install("docbook-xsl")
util.create_file(HOME_DIR / ".mutt" / "certificates")
util.create_dir(HOME_DIR / ".mutt" / "cache" / "bodies")
util.create_dir(HOME_DIR / ".mutt" / "cache" / "headers")

util.create_symlinks(
    [
        (PKG_DIR / filename, HOME_DIR / ".mutt" / filename)
        for filename in ["file_email", "colors.muttrc", "muttrc", "mailcap"]
    ]
)
