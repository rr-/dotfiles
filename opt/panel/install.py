from dotinstall import packages
from dotinstall import util


def run():
    packages.try_install('libxkbcommon-x11')
    packages.try_install('python-pyqt5')

    util.create_symlink('./panel', '~/.local/bin/')
    util.run_verbose(['sudo', 'pip', 'install', '-r', 'panel/requirements.txt'])
