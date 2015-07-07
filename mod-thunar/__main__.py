#!/bin/python
import os
from libinstall import PackageInstaller, run_silent

PackageInstaller.try_install('thunar')
PackageInstaller.try_install('xfconf')

if 'DISPLAY' in os.environ:
    #enable full path in thunar window title for scripting
    run_silent(['xfconf-query',
        '--channel', 'thunar',
        '--property', '/misc-full-path-in-title',
        '--create',
        '--type', 'bool',
        '--set', 'true'])
