from dotinstall import packages, util


def run():
    if util.distro_name() == "arch":
        packages.try_install("fzf")  # super opener
        packages.try_install(
            "silver-searcher-git"
        )  # super grep (vim-fzf dependency)
        packages.try_install("ripgrep")  # super grep (shell)
    elif util.distro_name() == "linuxmint":
        packages.try_install("silversearcher-ag")
        if not packages.has_installed("ripgrep"):
            util.run_verbose(
                [
                    "curl",
                    "-LO",
                    "https://github.com/BurntSushi/ripgrep/releases/download/11.0.2/ripgrep_11.0.2_amd64.deb",
                ]
            )
            util.run_verbose(
                ["sudo", "dpkg", "-i", "ripgrep_11.0.2_amd64.deb"]
            )

    util.create_symlink("./agignore", "~/.agignore")
