from dotinstall import packages
from dotinstall import util


def run():
    packages.try_install('weechat')
    util.create_symlink('./alias.conf', '~/.weechat/')
    util.create_symlink('./charset.conf', '~/.weechat/')
    util.create_symlink('./exec.conf', '~/.weechat/')
    util.create_symlink('./irc.conf', '~/.weechat/')
    util.create_symlink('./logger.conf', '~/.weechat/')
    util.create_symlink('./relay.conf', '~/.weechat/')
    util.create_symlink('./plugins.conf', '~/.weechat/')
    util.create_symlink('./script.conf', '~/.weechat/')
    util.create_symlink('./trigger.conf', '~/.weechat/')
    util.create_symlink('./weechat.conf', '~/.weechat/')
    util.create_symlink('./buffers.conf', '~/.weechat/')
    util.create_symlink('./buffer_autoset.conf', '~/.weechat/')
    util.create_symlink('./python/custom_hotlist.py', '~/.weechat/python/')
    util.create_symlink(
        './python/custom_hotlist.py', '~/.weechat/python/autoload/')
