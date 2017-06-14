#!/usr/bin/env python3
import os
import sys
import re
import argparse
import glob


ESC = '\033'
BEL = '\007'
DSC = ESC + 'P'
OSC = ESC + ']'


def change_color(name, arg):
    result = re.match(r'color(\d+)', name)
    if result:
        send_osc(4, int(result.group(1)), arg)
    elif name == 'foreground': send_osc(10, arg)
    elif name == 'background': send_osc(11, arg)
    elif name == 'cursor': send_osc(12, arg)
    elif name == 'mouse_foreground': send_osc(13, arg)
    elif name == 'mouse_background': send_osc(14, arg)
    elif name == 'highlight': send_osc(17, arg)
    elif name == 'border': send_osc(708, arg)
    else: raise ValueError('Unknown name: ' + name)


def send_escape_sequence(escape_sequence):
    escape_sequence = DSC + 'tmux;' + ESC + escape_sequence + ESC + '\\'
    sys.stdout.write(escape_sequence)


def send_osc(ps, *pt):
    command = OSC + str(ps) + ';' + ';'.join(str(x) for x in pt) + BEL
    send_escape_sequence(command)


def parse_args():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command_name')
    subparsers.add_parser('restore')
    subparsers.add_parser('list')
    subparsers.add_parser('get')
    subparsers.add_parser('cycle')
    set_parser = subparsers.add_parser('set')
    set_parser.add_argument('theme')
    return parser.parse_args()


def get_theme_names():
    paths = glob.glob('*.txt')
    result = []
    for path in paths:
        name, ext = os.path.splitext(os.path.basename(path))
        if name != 'current_scheme':
            result.append(name)
    return list(sorted(result))


def get_theme_path(name):
    return name + '.txt'


def apply_theme(theme_name):
    with open(get_theme_path(theme_name), 'r') as handle:
        for line in handle:
            if line.startswith('#'):
                continue
            match = re.match(r'\s*(.+?)\s*[=:]\s*(.+?)\s*$', line)
            if not match:
                continue
            key, value = match.groups()
            change_color(key, value)
    with open('current_scheme.txt', 'w') as handle:
        handle.write(theme_name)


def main():
    args = parse_args()
    os.chdir(os.path.realpath(os.path.dirname(__file__)))

    theme_names = get_theme_names()
    if not theme_names:
        print('No themes', file=sys.stderr)
        sys.exit(1)

    try:
        with open('current_scheme.txt', 'r') as handle:
            active_theme = handle.read()
    except IOError:
        active_theme = theme_names[0]
    if active_theme not in theme_names:
        print('Invalid theme', file=sys.stderr)
        sys.exit(1)

    if args.command_name == 'restore':
        apply_theme(active_theme)
    elif args.command_name == 'list':
        print('\n'.join(theme_names))
    elif args.command_name == 'get':
        print(active_theme)
    elif args.command_name == 'set':
        apply_theme(args.theme)
    elif args.command_name == 'cycle':
        current_theme_idx = theme_names.index(active_theme)
        next_theme_idx = (current_theme_idx + 1) % len(theme_names)
        next_theme_name = theme_names[next_theme_idx]
        apply_theme(next_theme_name)
    else:
        print('No command chosen', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
