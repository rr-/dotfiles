from dotinstall import packages, util


def run():
    packages.try_install("fzf")  # super opener
    packages.try_install(
        "silver-searcher-git"
    )  # super grep (vim-fzf dependency)
    packages.try_install("ripgrep")  # super grep (shell)
    util.create_symlink("./agignore", "~/.agignore")
