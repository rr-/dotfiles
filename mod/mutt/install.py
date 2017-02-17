from dotinstall import packages
from dotinstall import util


def run():
    packages.try_install('neomutt')
    util.create_file('~/.mutt/certificates')
    util.create_dir('~/.mutt/cache/bodies')
    util.create_dir('~/.mutt/cache/headers')
    util.create_symlink('./file_email', '~/.mutt/')
    util.create_symlink('./colors.muttrc', '~/.mutt/')
    util.create_symlink('./muttrc', '~/.mutt/')
