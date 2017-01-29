from dotinstall import packages
from dotinstall import util


def _make_default():
    # qutebrowser issue 22
    util.create_symlink('./qutebrowser.desktop', '~/.local/share/application/')
    util.run_verbose(
        ['xdg-settings', 'set', 'default-web-browser', 'qutebrowser.desktop'])
    util.run_verbose(
        ['xdg-mime', 'default', 'qutebrowser.desktop', 'text/html'])

    # XXX: this is huge bullshit and shouldn't be symlinked but i'm not going
    # to write a proper parser for xdg configuration when all I want is just to
    # install a fucking browser
    util.create_symlink('./mimeapps.list', '~/.config/')


def run():
    packages.try_install('qutebrowser')
    util.create_symlink('./qutebrowser', '~/.config/')
    _make_default()
