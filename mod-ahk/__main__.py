#!/bin/python3
from libinstall import FileInstaller, run_silent
import os
import tempfile
import urllib.request
dir = os.path.dirname(__file__)

def install_autohotkey():
    install_path = os.path.join(tempfile.gettempdir(), 'ahk-install.exe')

    if not os.path.exists(install_path):
        url = 'http://ahkscript.org/download/ahk-install.exe'
        response = urllib.request.urlopen(url)
        data = response.read()
        with open(install_path, 'wb') as f:
            f.write(data)

    os.chmod(install_path, 0o777)
    if not run_silent([install_path, '/s'])[0]:
        raise RuntimeError('Failed to install AutoHotkey')

    os.unlink(install_path)

install_autohotkey()

script_path = os.path.join(dir, 'hk.ahk')
if FileInstaller.has_executable('cygpath'):
    script_path = run_silent(['cygpath', '-w', script_path])[1].strip()

run_silent([
    'reg',
    'add', 'HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run',
    '/v', 'AutoHotkey',
    '/t', 'REG_SZ',
    '/f',
    '/d', script_path])
