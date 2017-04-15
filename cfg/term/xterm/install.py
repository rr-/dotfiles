from os.path import expanduser
from dotinstall import packages
from dotinstall import util


def run():
    packages.try_install('xterm')

    util.create_symlink('./Xresources', '~/.config/Xresources')
    util.run_verbose(['xrdb', '-override', expanduser('~/.config/Xresources')])
