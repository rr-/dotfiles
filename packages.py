import sys
import logging
import tempfile
import re
import util

logger = logging.getLogger(__name__)

class CygwinPackageInstaller(object):
    name = 'cygwin'

    @property
    def supported(self):
        return util.has_executable('apt-cyg')

    def has_installed(self, package):
        return len(util.run_silent(['apt-cyg', 'list', '^%s$' % package])[1]) > 0

    def is_available(self, package):
        return len(util.run_silent(['apt-cyg', 'listall', '^%s$' % package])[1]) > 0

    def install(self, package):
        return util.run_verbose(['apt-cyg', 'install', package])

class PacmanPackageInstaller(object):
    name = 'pacman'

    @property
    def supported(self):
        return util.has_executable('pacman') and util.has_executable('sudo')

    def has_installed(self, package):
        return util.run_silent(['pacman', '-Q', package])[0]

    def is_available(self, package):
        return util.run_silent(['pacman', '-Ss', package])[0]

    def install(self, package):
        return util.run_verbose(['sudo', 'pacman', '-S', package])

class YaourtPackageInstaller(object):
    name = 'yaourt'

    @property
    def supported(self):
        return util.has_executable('yaourt') and util.has_executable('sudo')

    def has_installed(self, package):
        return util.run_silent(['yaourt', '-Q', package])[0]

    def is_available(self, package):
        return util.run_silent(['yaourt', '-Ss', package])[0]

    def install(self, package):
        return util.run_verbose(['yaourt', '-S', package])

class PipPackageInstaller(object):
    name = 'pip'
    cache_dir = tempfile.gettempdir()

    def __init__(self):
        if 'cygwin' in sys.platform:
            self.executable = 'pip3'
            self.use_sudo = False
        else:
            self.executable = 'pip'
            self.use_sudo = True

    @property
    def supported(self):
        if self.use_sudo and not util.has_executable('sudo'):
            return False
        return util.has_executable(self.executable)

    def has_installed(self, package):
        return re.search(
            '^' + re.escape(package) + r'($|\s)',
            util.run_silent([self.executable, 'list'])[1],
            re.MULTILINE) is not None

    def is_available(self, package):
        return re.search(
            '^' + re.escape(package) + r'($|\s)',
            util.run_silent([self.executable, 'search', package, '--cache-dir', self.cache_dir])[1],
            re.MULTILINE) is not None

    def install(self, package):
        command = [self.executable, 'install', '--cache-dir', self.cache_dir, package]
        if self.use_sudo:
            command = ['sudo'] + command
        return util.run_verbose(command)

INSTALLERS = [
    CygwinPackageInstaller(),
    PacmanPackageInstaller(),
    YaourtPackageInstaller(),
    PipPackageInstaller(),
]

def try_install(package, method=None):
    try:
        install(package, method)
    except Exception as ex:
        logger.info('Error installing %s: %s', package, ex)

def has_installed(package, method=None):
    chosen_installers = _choose_installers(method)
    for installer in chosen_installers:
        if installer.has_installed(package):
            return True
    return False

def install(package, method=None):
    if has_installed(package, method):
        logger.info('Package %s is already installed.', package)
        return True
    chosen_installers = _choose_installers(method)
    for installer in chosen_installers:
        if installer.is_available(package):
            logger.info('Package %s is available, installing with %s', package, installer.name)
            return installer.install(package)
    if method is None:
        raise RuntimeError('No package manager is capable of installing %s', package)
    else:
        raise RuntimeError('%s is not capable of installing %s', method, package)

def _choose_installers(method):
    if method is None:
        chosen_installers = INSTALLERS
    else:
        chosen_installers = [i for i in INSTALLERS if i.name == method]
    chosen_installers = [i for i in chosen_installers if i.supported]
    if len(chosen_installers) == 0:
        if method is None:
            raise RuntimeError('No package manager is supported on this system!')
        else:
            raise RuntimeError('%s is not supported on this system!', method)
    return chosen_installers
