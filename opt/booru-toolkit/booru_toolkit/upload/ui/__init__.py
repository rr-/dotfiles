import urwid
from booru_toolkit.upload.ui.ui import run

del urwid.command_map['left']
del urwid.command_map['down']
del urwid.command_map['up']
del urwid.command_map['right']
