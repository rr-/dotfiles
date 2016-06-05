import os
import logs
import packages
import util

packages.try_install('xorg-font-utils')
packages.try_install('otf-ipafont')
packages.try_install('ttf-dejavu')
packages.try_install('ttf-symbola')
packages.try_install('ttf-font-awesome')
packages.try_install('ttf-monapo')

if os.path.exists('/usr/share/fonts'):
    fonts_dir = '~/.local/share/fonts/'

    util.create_dir(fonts_dir)
    for font_path in util.find('#/*.ttf'):
        util.create_symlink(font_path, fonts_dir)

    if util.has_executable('mkfontscale'):
        util.run_verbose(['mkfontscale', util.expand_path(fonts_dir)])
    if util.has_executable('mkfontdir'):
        util.run_verbose(['mkfontdir', util.expand_path(fonts_dir)])
    if util.has_executable('xset'):
        util.run_verbose(['xset', '+fp', util.expand_path(fonts_dir)])
        util.run_verbose(['xset', 'fp', 'rehash'])

if util.has_executable('fc-cache'):
    util.create_symlink('#/fonts.conf', '~/.config/fontconfig/')
    util.run_verbose(['fc-cache'])
