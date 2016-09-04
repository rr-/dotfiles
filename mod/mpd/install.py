import packages
import util


def run():
    if not packages.try_install('mpd-light'):
        packages.try_install('mpd')
    packages.try_install('mpc')

    util.create_symlink('./config', '~/.config/mpd')
    util.create_dir('~/.config/mpd/playlists')
    for file in ['database', 'log', 'pid', 'state', 'sticker.sql']:
        util.create_file('~/.config/mpd/' + file)
    util.create_symlink('./start', '~/.config/x/start-mpd.sh')
