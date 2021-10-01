from pathlib import Path

from libdotfiles import HOME_DIR, PKG_DIR, packages, util

FZF_DIR = HOME_DIR / ".fzf"

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
        util.run_verbose(["sudo", "dpkg", "-i", "ripgrep_11.0.2_amd64.deb"])

    util.run_verbose(
        [
            "git",
            "clone",
            "--depth",
            "1",
            "https://github.com/junegunn/fzf.git",
            FZF_DIR,
        ]
    )
    util.run_verbose(
        [
            FZF_DIR / "install",
            "--key-bindings",
            "--completion",
            "--no-update-rc",
        ]
    )

util.create_symlink(PKG_DIR / "agignore", HOME_DIR / ".agignore")
