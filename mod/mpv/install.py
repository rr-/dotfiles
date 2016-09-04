import packages
import util


def run():
    packages.try_install('luajit')
    if not util.has_executable('mpv'):
        packages.try_install('mpv-git')
    util.create_symlink('./config', '~/.config/mpv')
