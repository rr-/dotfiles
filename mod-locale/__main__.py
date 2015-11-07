#!/bin/python
import os, glob
from libinstall import FileInstaller, PackageInstaller, run_verbose
dir = os.path.dirname(__file__)

FileInstaller.create_symlink(os.path.join(dir, 'locale.conf'), '~/.config/')
run_verbose(['sudo', 'sh', '-c', 'sed -i "s/#en_US.UTF-8/en_US.UTF-8/" /etc/locale.gen'])
run_verbose(['sudo', 'sh', '-c', 'sed -i "s/#pl_PL.UTF-8/pl_PL.UTF-8/" /etc/locale.gen'])
run_verbose(['sudo', 'sh', '-c', 'sed -i "s/#ja_JP.UTF-8/ja_JP.UTF-8/" /etc/locale.gen'])
run_verbose(['sudo', 'locale-gen'])
