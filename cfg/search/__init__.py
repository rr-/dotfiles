from pathlib import Path

from libdotfiles import packages, util


def run() -> None:
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

        fzf_dir = Path("~/.fzf").expanduser()
        util.run_verbose(
            [
                "git",
                "clone",
                "--depth",
                "1",
                "https://github.com/junegunn/fzf.git",
                fzf_dir,
            ]
        )
        util.run_verbose(
            [
                fzf_dir / "install",
                "--key-bindings",
                "--completion",
                "--no-update-rc",
            ]
        )

    util.create_symlink("./agignore", "~/.agignore")
