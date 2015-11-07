#!/bin/python
import os, glob
from libinstall import FileInstaller, PackageInstaller, run_verbose
dir = os.path.dirname(__file__)

PackageInstaller.try_install('xorg-font-utils')
PackageInstaller.try_install('ttf-dejavu')
PackageInstaller.try_install('ttf-symbola')
PackageInstaller.try_install('ttf-font-awesome')
PackageInstaller.try_install('ttf-monapo')

if os.path.exists('/usr/share/fonts'):
    fonts_dir = os.path.expanduser('~/.local/share/fonts')

    FileInstaller.create_dir(fonts_dir)
    for font_path in glob.glob(os.path.join(dir, '*.ttf')):
        FileInstaller.create_symlink(font_path, fonts_dir + '/')

    if FileInstaller.has_executable('mkfontscale'):
        run_verbose(['mkfontscale', fonts_dir])
    if FileInstaller.has_executable('mkfontdir'):
        run_verbose(['mkfontdir', fonts_dir])
    if FileInstaller.has_executable('xset'):
        run_verbose(['xset', '+fp', fonts_dir])
        run_verbose(['xset', 'fp', 'rehash'])

if FileInstaller.has_executable('fc-cache'):
    FileInstaller.create_symlink(os.path.join(dir, 'fonts.conf'), '~/.config/fontconfig/')
    run_verbose(['fc-cache'])
