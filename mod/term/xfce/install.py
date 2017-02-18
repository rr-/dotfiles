from dotinstall import packages
from dotinstall import util


def run():
    packages.try_install('xfce4-terminal')
    util.create_symlink('./config', '~/.config/xfce4/terminal')
