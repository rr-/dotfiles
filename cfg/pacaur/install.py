import os
from dotinstall import packages
from dotinstall import util


def run():
    os.chdir('/tmp')
    util.run_verbose(['git', 'clone', 'https://aur.archlinux.org/cower.git'])
    os.chdir('/tmp/cower')
    util.run_verbose(['makepkg', '-i', '--skippgpcheck'])

    packages.install('expac', method='pacman')

    os.chdir('/tmp')
    util.run_verbose(['git', 'clone', 'https://aur.archlinux.org/pacaur.git'])
    os.chdir('/tmp/pacaur')
    util.run_verbose(['makepkg', '-i', '--skippgpcheck'])
