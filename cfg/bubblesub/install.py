import os
from dotinstall import packages
from dotinstall import util


def run():
    packages.try_install('python-pyqt5')
    packages.try_install('ffms2000-git')
    packages.try_install('fftw')
    # packages.try_install('bubblesub')

    util.create_symlink('./scripts', '~/.config/bubblesub/')
