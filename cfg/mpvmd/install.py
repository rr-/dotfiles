from dotinstall import packages
from dotinstall import util


def run():
    if not util.has_executable('mpv'):
        packages.try_install('luajit')
        packages.try_install('mpv')
    util.create_symlink('./config', '~/.config/mpvmd')
    util.create_symlink('./mpvmd', '~/.local/bin/')
    util.create_symlink('./mpvmc', '~/.local/bin/')
    util.create_symlink('./mpvmd.service', '~/.config/systemd/user/')
