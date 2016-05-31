from libinstall import run_verbose, run_silent, FileInstaller, PackageInstaller
import os
import tarfile
import urllib.request

def install_aur(package):
    if PackageInstaller.is_installed(package):
        print(package, 'already installed')
        return
    old_dir = os.getcwd()
    os.chdir('/tmp')
    url = 'https://aur.archlinux.org/cgit/aur.git/snapshot/{0}.tar.gz'.format(package)
    urllib.request.urlretrieve(url, 'tmp.tar')
    tar = tarfile.open('tmp.tar')
    tar.extractall()
    os.chdir(os.path.join('/tmp', package))
    run_verbose(['makepkg', '-i'])
    os.chdir(old_dir)

PackageInstaller.install('sudo')
PackageInstaller.install('tar')
PackageInstaller.install('wget')
PackageInstaller.install('gcc')       # to compile everything
PackageInstaller.install('make')      # to compile everything
PackageInstaller.install('fakeroot')  # for package-query
PackageInstaller.install('yajl')      # for package-query
PackageInstaller.install('binutils')  # for yaourt

install_aur('package-query')
install_aur('yaourt')
