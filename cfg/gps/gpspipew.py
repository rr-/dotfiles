#!/usr/bin/env python
import sys
from os import environ
from os.path import dirname, realpath
from struct import pack
from subprocess import PIPE, Popen

"""
Wraps gpspipe in order to pass Chrome Native Messaging protocol messages.

Copyright 2016-2017 Michael Farrell <micolous+git@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.


gpspipe must be in your PATH for this script to work.

ref: https://developer.chrome.com/extensions/nativeMessaging
"""

# Make a copy of the environment, and stuff in extra places to try.
# On OSX, $PATH when launched from the Dock or Finder is sparse.
env = environ.copy()
env["PATH"] = ":".join(
    [
        env["PATH"],
        dirname(realpath(__file__)),
        "/usr/local/bin",
        "/usr/bin",
    ]
)

process = Popen(["gpspipe", "-w"], stdin=PIPE, stdout=PIPE, env=env)

try:
    assert process.stdout
    while process.returncode is None:
        process.poll()
        line = process.stdout.readline()

        if len(line) == 0:
            # Drop empty lines
            continue

        line = line.strip()

        # Protocol is to have a JSON blob preceeded with a uint32 in native byte
        # order.
        sys.stdout.buffer.write(pack("=L", len(line)) + line)
        sys.stdout.buffer.flush()
except KeyboardInterrupt:
    pass
finally:
    try:
        process.kill()
    except Exception:
        pass
