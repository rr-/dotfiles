from pathlib import Path
from typing import cast

import requests

from libdotfiles.packages import has_installed, try_install
from libdotfiles.util import get_distro_name, run


def sudo_write(target_path: Path, content: bytes) -> None:
    run(
        ["sudo", "tee", str(target_path)],
        input=content,
        capture_output=True,
        check=True,
    )


def setup_ubuntu_mpr() -> None:
    gpg_path = Path("/usr/share/keyrings/prebuilt-mpr-archive-keyring.gpg")
    list_path = Path("/etc/apt/sources.list.d/prebuilt-mpr.list")

    if not list_path.exists():
        arch = run(
            ["dpkg", "--print-architecture"], capture_output=True, text=True
        ).stdout.strip()
        lsb_release = run(
            ["lsb_release", "-cs"], capture_output=True, text=True
        ).stdout.strip()

        sudo_write(
            list_path,
            f"deb [arch=all,{arch} "
            f"signed-by=/usr/share/keyrings/prebuilt-mpr-archive-keyring.gpg] "
            f"https://proget.makedeb.org prebuilt-mpr {lsb_release}".encode(),
        )

    if not gpg_path.exists():
        pubkey_response = requests.get(
            "https://proget.makedeb.org/debian-feeds/prebuilt-mpr.pub"
        )
        pubkey_str = pubkey_response.text
        pubkey_bytes = cast(
            bytes,
            run(
                ["gpg", "--dearmor"],
                input=pubkey_str.encode(),
                capture_output=True,
                check=True,
            ).stdout,
        )

        sudo_write(gpg_path, pubkey_bytes)


if not has_installed("just"):
    if get_distro_name() == "arch":
        try_install("just", method="pacman")
    else:
        setup_ubuntu_mpr()
        run(["sudo", "apt-get", "update"], check=True)
        run(["sudo", "apt-get", "install", "-y", "just"], check=True)
