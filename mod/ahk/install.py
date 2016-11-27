import os
import tempfile
from dotfiles import logging
from dotinstall import util

logger = logging.getLogger(__name__)


def install_autohotkey():
    install_path = os.path.join(tempfile.gettempdir(), 'ahk-install.exe')

    if not os.path.exists(install_path):
        url = 'http://ahkscript.org/download/ahk-install.exe'
        util.download(url, install_path)

    os.chmod(install_path, 0o777)
    if not util.run_silent([install_path, '/s'])[0]:
        raise RuntimeError('Failed to install AutoHotkey')

    os.unlink(install_path)


def run():
    try:
        install_autohotkey()
    except Exception as ex:
        logger.error(ex)

    script_path = util.expand_path('./hk.ahk')
    if util.has_executable('cygpath'):
        script_path = util.run_silent(
            ['cygpath', '-w', script_path])[1].strip()

    logger.info('Adding script to autostart')
    util.run_silent([
        'reg',
        'add', r'HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run',
        '/v', 'AutoHotkey',
        '/t', 'REG_SZ',
        '/f',
        '/d', script_path])
