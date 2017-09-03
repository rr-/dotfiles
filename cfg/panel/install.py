import os
from dotinstall import packages
from dotinstall import util


def run():
    packages.try_install('libxkbcommon-x11')
    packages.try_install('python-pyqt5')

    util.copy_file('./start', '~/.config/x/start-panel.sh')

    os.chdir(util.root_dir / 'opt' / 'panel')
    util.run_verbose(['pip', 'install', '--user', '--upgrade', '.'])
