from dotinstall import packages
from dotinstall import util


def run():
    packages.try_install('sxhkd-git')
    packages.try_install('xdo-git')

    util.create_symlink('./config', '~/.config/sxhkd')
    util.create_symlink('./beep-shot.mp3', '~/.local/share/')
    util.create_symlink('./start', '~/.config/x/start-sxhkd.sh')
