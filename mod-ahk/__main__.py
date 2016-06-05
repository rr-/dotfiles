import os
import tempfile
import logs
import util

def install_autohotkey():
    install_path = os.path.join(tempfile.gettempdir(), 'ahk-install.exe')

    if not os.path.exists(install_path):
        url = 'http://ahkscript.org/download/ahk-install.exe'
        util.download(url, install_path)

    os.chmod(install_path, 0o777)
    if not util.run_silent([install_path, '/s'])[0]:
        raise RuntimeError('Failed to install AutoHotkey')

    os.unlink(install_path)

install_autohotkey()

script_path = util.expand_path('#/hk.ahk')
if util.has_executable('cygpath'):
    script_path = util.run_silent(['cygpath', '-w', script_path])[1].strip()

util.run_silent([
    'reg',
    'add', 'HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run',
    '/v', 'AutoHotkey',
    '/t', 'REG_SZ',
    '/f',
    '/d', script_path])
