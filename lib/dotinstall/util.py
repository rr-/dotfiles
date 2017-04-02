import os
import shutil
import logging
import glob
from subprocess import Popen, call, PIPE
import urllib.request

logger = logging.getLogger(__name__)


def run_silent(*args, **kwargs):
    proc = Popen(stdout=PIPE, stderr=PIPE, *args, **kwargs)
    out, err = proc.communicate()
    try:
        out, err = out.decode('utf8'), err.decode('utf8')
    except UnicodeDecodeError:
        pass
    return (proc.returncode == 0, out, err)


def run_verbose(*args, **kwargs):
    return call(*args, **kwargs) == 0


def has_executable(program):
    return shutil.which(program) is not None


def assert_has_executable(program):
    if not has_executable(program):
        raise RuntimeError('%s not installed, cannot proceed', program)


def expand_path(path, source=None):
    is_dir = path.endswith('/') or path.endswith('\\')
    target = os.path.abspath(os.path.expanduser(path))
    if is_dir and source:
        target = os.path.join(target, os.path.basename(source))
    return target


def abs_path(path):
    return os.path.abspath(expand_path(path))


def find(path):
    path = abs_path(path)
    if os.path.isdir(path):
        return glob.glob(os.path.join(path, '*'))
    return glob.glob(path)


def download(url, path, overwrite=False):
    path = expand_path(path)
    if os.path.isdir(path):
        path = os.path.join(path, os.path.basename(url))
    create_dir(os.path.dirname(path))
    if overwrite or not os.path.exists(path):
        logger.info('Downloading %r into %r...', url, path)
        request = urllib.request.Request(url)
        request.add_header('User-Agent', 'mozilla')
        request.add_header('Referer', url)
        response = urllib.request.urlopen(request)
        with open(path, 'wb') as handle:
            handle.write(response.read())


def exists(path):
    path = expand_path(path)
    return os.path.exists(path)


def create_file(path, content=None, overwrite=False):
    path = expand_path(path)
    dir_path = os.path.dirname(path)
    create_dir(dir_path)
    if overwrite or not os.path.exists(path):
        logger.info('Creating file %r...', path)
        with open(path, 'w') as handle:
            if content:
                handle.write(content)


def create_dir(path):
    path = expand_path(path)
    if not os.path.exists(path):
        logger.info('Creating directory %r...', path)
        os.makedirs(path)


def copy_file(source, target):
    source = expand_path(source)
    target = expand_path(target, source)
    _remove_symlink(target)
    logger.info('Copying %r to %r...', source, target)
    create_dir(os.path.dirname(target))
    shutil.copy(source, target)


def create_symlink(source, target):
    source = expand_path(source)
    target = expand_path(target, source)
    _remove_symlink(target)
    if os.path.exists(target):
        raise RuntimeError(
            'Target file %r exists and is not a symlink.', target)
    logger.info('Linking %r to %r...', source, target)
    create_dir(os.path.dirname(target))
    os.symlink(source, target)


def _remove_symlink(path):
    if os.path.islink(path):
        logger.info('Removing old symlink %r...', path)
        os.unlink(path)
