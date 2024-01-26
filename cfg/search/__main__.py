from libdotfiles.packages import has_installed, try_install
from libdotfiles.util import (
    HOME_DIR,
    PKG_DIR,
    create_symlink,
    get_distro_name,
    run,
)

FZF_DIR = HOME_DIR / ".fzf"

if get_distro_name() in ["arch", "ubuntu"]:
    try_install("fzf")  # super opener
    try_install("ripgrep")  # super grep

elif get_distro_name() == "linuxmint":
    if not has_installed("ripgrep"):
        run(
            [
                "curl",
                "-LO",
                "https://github.com/BurntSushi/ripgrep/releases/download/11.0.2/ripgrep_11.0.2_amd64.deb",
            ],
            check=True,
        )
        run(["sudo", "dpkg", "-i", "ripgrep_11.0.2_amd64.deb"], check=True)

    run(
        [
            "git",
            "clone",
            "--depth",
            "1",
            "https://github.com/junegunn/fzf.git",
            FZF_DIR,
        ],
        check=True,
    )
    run(
        [
            FZF_DIR / "install",
            "--key-bindings",
            "--completion",
            "--no-update-rc",
        ],
        check=True,
    )

create_symlink(PKG_DIR / "agignore", HOME_DIR / ".agignore")
