import os
import logging
import tarfile
import util
import logs
import packages

logger = logging.getLogger(__name__)

def install_aur(package):
    if packages.has_installed(package):
        logger.info('%s already installed', package)
        return
    old_dir = os.getcwd()
    os.chdir('/tmp')
    url = 'https://aur.archlinux.org/cgit/aur.git/snapshot/{0}.tar.gz'.format(package)
    util.download(url, '/tmp/tmp.tar')
    tar = tarfile.open('tmp.tar')
    tar.extractall()
    os.chdir(os.path.join('/tmp', package))
    run_verbose(['makepkg', '-i'])
    os.chdir(old_dir)

packages.install('sudo')
packages.install('tar')
packages.install('wget')
packages.install('gcc')       # to compile everything
packages.install('make')      # to compile everything
packages.install('fakeroot')  # for package-query
packages.install('yajl')      # for package-query
packages.install('binutils')  # for yaourt

install_aur('package-query')
install_aur('yaourt')
util.create_symlink('#/yaourtrc', '~/.yaourtrc')
