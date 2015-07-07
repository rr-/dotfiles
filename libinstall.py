import os
import re
import shutil
import subprocess
import sys
import tempfile

def run_silent(p):
    proc = subprocess.Popen(p, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    out, err = out.decode('utf8'), err.decode('utf8')
    return (proc.returncode == 0, out, err)

def run_verbose(p):
    return subprocess.call(p) == 0

class FileInstaller(object):
    @staticmethod
    def confirm_executable(program):
        if not FileInstaller.has_executable(program):
            raise RuntimeError('%s not installed, cannot proceed' % program)

    @staticmethod
    def has_executable(program):
        return shutil.which(program) is not None

    @staticmethod
    def create_dir(dir):
        if os.path.islink(dir):
            print('Removing old symlink...')
            os.unlink(dir)
        if not os.path.exists(dir):
            print('Creating directory %s...' % dir)
            os.makedirs(dir)

    @staticmethod
    def create_file(path):
        dir = os.path.dirname(path)
        if not os.path.islink(dir):
            FileInstaller.create_dir(dir)
        if not os.path.exists(path):
            print('Creating file %s...' % path)
            with open(path, 'wb'):
                pass

    @staticmethod
    def copy_file(source, target):
        source = os.path.abspath(os.path.expanduser(source))
        target = os.path.expanduser(target)
        if target.endswith('/') or target.endswith('\\'):
            target = os.path.join(target, os.path.basename(source))

        if os.path.islink(target):
            print('Removing old symlink...')
            os.unlink(target)

        print('Copying %s to %s...' % (source, target))
        FileInstaller.create_dir(os.path.dirname(target))
        shutil.copy(source, target)

    @staticmethod
    def create_symlink(source, target):
        source = os.path.abspath(os.path.expanduser(source))
        target = os.path.expanduser(target)
        if target.endswith('/') or target.endswith('\\'):
            target = os.path.join(target, os.path.basename(source))

        if os.path.islink(target):
            print('Removing old symlink...')
            os.unlink(target)
        elif os.path.exists(target):
            raise RuntimeError('Target file %s exists and is not a symlink.' % target)

        print('Linking %s to %s...' % (source, target))
        FileInstaller.create_dir(os.path.dirname(target))
        os.symlink(source, target)

class CygwinPackageInstaller(object):
    name = 'cygwin'

    def supported(self):
        return FileInstaller.has_executable('apt-cyg')

    def is_installed(self, package):
        return len(run_silent(['apt-cyg', 'list', '^%s$' % package])[1]) > 0

    def is_available(self, package):
        return len(run_silent(['apt-cyg', 'listall', '^%s$' % package])[1]) > 0

    def install(self, package):
        return run_verbose(['apt-cyg', 'install', package])

class PacmanPackageInstaller(object):
    name = 'pacman'

    def supported(self):
        return FileInstaller.has_executable('pacman') and FileInstaller.has_executable('sudo')

    def is_installed(self, package):
        return run_silent(['pacman', '-Q', package])[0]

    def is_available(self, package):
        return run_silent(['pacman', '-Ss', package])[0]

    def install(self, package):
        return run_verbose(['sudo', 'pacman', '-S', package])

class YaourtPackageInstaller(object):
    name = 'yaourt'

    def supported(self):
        return FileInstaller.has_executable('yaourt') and FileInstaller.has_executable('sudo')

    def is_installed(self, package):
        return run_silent(['yaourt', '-Q', package])[0]

    def is_available(self, package):
        return run_silent(['yaourt', '-Ss', package])[0]

    def install(self, package):
        return run_verbose(['yaourt', '-S', package])

class PipPackageInstaller(object):
    name = 'pip'
    cache_dir = tempfile.gettempdir()

    def supported(self):
        return FileInstaller.has_executable('pip') and FileInstaller.has_executable('sudo')

    def is_installed(self, package):
        return re.search(
            '^' + re.escape(package) + '($|\s)',
            run_silent(['pip', 'list'])[1],
            re.MULTILINE) is not None

    def is_available(self, package):
        return re.search(
            '^' + re.escape(package) + '($|\s)',
            run_silent(['pip', 'search', package, '--cache-dir', self.cache_dir])[1],
            re.MULTILINE) is not None

    def install(self, package):
        return run_verbose(['sudo', 'pip', 'install', '--cache-dir', self.cache_dir, package])

class PackageInstaller(object):
    INSTALLERS = {
        CygwinPackageInstaller(),
        PacmanPackageInstaller(),
        YaourtPackageInstaller(),
        PipPackageInstaller(),
    }

    @staticmethod
    def try_install(package, method=None):
        try:
            PackageInstaller.install(package, method)
        except Exception as e:
            print('Error installing %s: %s' % (package, e))

    @staticmethod
    def install(package, method=None):
        if method is None:
            chosen_installers = PackageInstaller.INSTALLERS
        else:
            chosen_installers = [i for i in PackageInstaller.INSTALLERS if i.name == method]

        chosen_installers = [i for i in chosen_installers if i.supported()]
        if len(chosen_installers) == 0:
            if method is None:
                raise RuntimeError('No package manager is supported on this system!')
            else:
                raise RuntimeError('%s is not supported on this system!' % method)

        for installer in chosen_installers:
            if installer.is_installed(package):
                print('Package %s is already installed.' % package)
                return True
            elif installer.is_available(package):
                print('Package %s is available, installing with %s' % (package, installer.name))
                return installer.install(package)

        if method is None:
            raise RuntimeError('No package manager is capable of installing %s' % package)
        else:
            raise RuntimeError('%s is not capable of installing %s' % (method, package))
