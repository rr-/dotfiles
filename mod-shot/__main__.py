#!/bin/python3
from libinstall import run_verbose
import os, sys
dir = os.path.dirname(__file__)
shot_dir = os.path.join(dir, 'shot')

if not os.path.exists(shot_dir):
    os.chdir(dir)
    run_verbose(['git', 'clone', 'https://github.com/rr-/shot.git'])
else:
    os.chdir(shot_dir)
    run_verbose(['git', 'pull'])

os.chdir(shot_dir)
run_verbose([os.path.join(shot_dir, 'bootstrap')])
if 'cygwin' in sys.platform:
    run_verbose([os.path.join(shot_dir, 'waf'), 'configure', '--prefix='])
else:
    run_verbose([os.path.join(shot_dir, 'waf'), 'configure'])

run_verbose([os.path.join(shot_dir, 'waf'), 'install'])
