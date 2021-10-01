from libdotfiles import util


def run() -> None:
    util.create_symlink("./inputrc", "~/.inputrc")
    util.create_symlink("./minttyrc", "~/.minttyrc")
