from dotinstall import packages, util


def run():
    if not util.has_executable("mpv"):
        packages.try_install("luajit")
        packages.try_install("mpv-git")
    util.create_symlink("./config", "~/.config/mpi")
    util.create_symlink("./mpi", "~/.local/bin/")
