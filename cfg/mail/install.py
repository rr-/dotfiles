from libdotfiles import packages, util


def run():
    packages.try_install("getmail")
    util.create_dir("~/mail/new")
    util.create_dir("~/mail/cur")
    util.create_dir("~/mail/tmp")

    packages.try_install("neomutt")
    packages.try_install("w3m")
    packages.try_install("lynx")
    packages.try_install("docbook-xsl")
    util.create_file("~/.mutt/certificates")
    util.create_dir("~/.mutt/cache/bodies")
    util.create_dir("~/.mutt/cache/headers")

    util.create_symlink("./file_email", "~/.mutt/")
    util.create_symlink("./colors.muttrc", "~/.mutt/")
    util.create_symlink("./muttrc", "~/.mutt/")
    util.create_symlink("./mailcap", "~/.mailcap")
