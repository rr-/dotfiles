from dotinstall import packages
from dotinstall import util


def run():
    packages.try_install('rtorrent')

    util.create_dir('~/hub/rtorrent/session')
    util.create_dir('~/hub/rtorrent/data')
    util.create_symlink('./rtorrent.rc', '~/.rtorrent.rc')

    # couldn't be bothered to create definition that ACTUALLY FUCKING WORKS
    # util.create_symlink(
    #     './rtorrent.service', '~/.config/systemd/user/rtorrent.service')
