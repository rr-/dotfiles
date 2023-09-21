import os
import tempfile

from libdotfiles.packages import try_install
from libdotfiles.util import HOME_DIR, get_distro_name, git_clone, run


def install_dict() -> None:
    git_clone("git@github.com:bubblesub/dict", HOME_DIR / "work/priv/dict")
    run(
        [
            "python3",
            "-m",
            "pip",
            "install",
            "--user",
            "--break-system-packages",
            ".",
        ],
        check=False,
        cwd=HOME_DIR / "work/priv/dict",
    )


def install_translate_shell() -> None:
    if get_distro_name() == "arch":
        try_install("translate-shell-git")
    elif get_distro_name() == "linuxmint":
        with tempfile.TemporaryDirectory() as tmp_dir:
            os.chdir(tmp_dir)
            run(
                ["git", "clone", "https://github.com/soimort/translate-shell"],
                check=True,
            )
            os.chdir("translate-shell")
            run(["make"], check=True)
            run(["sudo", "make", "install"], check=True)


install_dict()
install_translate_shell()
