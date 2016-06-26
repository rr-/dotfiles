import os
import yaml

path = os.path.expanduser('~/.config/dotfiles.yml')
with open(path, 'r') as handle:
    config = yaml.load(handle)
