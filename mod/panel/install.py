from dotinstall import util


def run():
    util.create_symlink('./panel', '~/.local/bin/')
    util.run_verbose(['sudo', 'pip', 'install', '-r', 'panel/requirements.txt'])
