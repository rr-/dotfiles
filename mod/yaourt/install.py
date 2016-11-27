import os
import shutil
from dotfiles import logging
from dotinstall import packages
from dotinstall import util

logger = logging.getLogger(__name__)


def install_aur(package):
    if packages.has_installed(package):
        logger.info('%s already installed', package)
        return
    old_dir = os.getcwd()
    root_dir = '/tmp/install-' + package
    os.makedirs(root_dir, exist_ok=True)
    os.chdir(root_dir)
    url = ('https://aur.archlinux.org/cgit/aur.git/plain/PKGBUILD?h=%s' %
        package)
    util.download(url, os.path.join(root_dir, 'PKGBUILD'))
    util.run_verbose(['makepkg', 'PKGBUILD', '--skippgpcheck'])
    util.run_verbose(['sudo', '-S', 'pacman', '-U', '--noconfirm',
        util.find(os.path.join(root_dir, '*.tar.xz'))[0]])
    shutil.rmtree(root_dir)
    os.chdir(old_dir)


def run():
    util.run_verbose(['sudo', '-S', 'pacman', '-Syu'])
    packages.install('sudo')
    packages.install('base-devel') # package-query
    packages.install('tar')
    packages.install('wget')
    packages.install('gcc')       # to compile everything
    packages.install('make')      # to compile everything
    packages.install('fakeroot')  # for package-query
    packages.install('yajl')      # for package-query
    packages.install('binutils')  # for yaourt

    install_aur('package-query')
    install_aur('yaourt')
    util.create_symlink('./yaourtrc', '~/.yaourtrc')
