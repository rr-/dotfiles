#!/bin/python
from libinstall import PackageInstaller, FileInstaller

PackageInstaller.try_install('make')
PackageInstaller.try_install('gcc')
PackageInstaller.try_install('automake')
PackageInstaller.try_install('lsof')

#TODO: move this to mod-vim
if FileInstaller.has_executable('devenv'):
    FileInstaller.copy('~/.vimrc', '~/.vsvimrc')
