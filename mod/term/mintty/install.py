import util


def run():
    util.create_symlink('./inputrc', '~/.inputrc')
    util.create_symlink('./minttyrc-dark', '~/.minttyrc-dark')
    util.create_symlink('./minttyrc-light', '~/.minttyrc-light')
    util.create_symlink('./minttyrc-light', '~/.minttyrc')
