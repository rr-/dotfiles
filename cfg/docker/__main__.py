import tempfile
from pathlib import Path

from libdotfiles.packages import try_install
from libdotfiles.util import (
    current_username,
    download_file,
    get_distro_name,
    run,
)

if get_distro_name() == "linux":
    try_install("docker")
    try_install("docker-compose")
elif get_distro_name() == "linuxmint":
    with tempfile.TemporaryDirectory() as tmpdir:
        target_file = Path(tmpdir) / "docker-key.gpg"
        download_file(
            "https://download.docker.com/linux/ubuntu/gpg", target_file
        )
        run(["sudo", "apt-key", "add", target_file], check=False)

    run(
        [
            "sudo",
            "add-apt-repository",
            "deb [arch=amd64] https://download.docker.com/linux/ubuntu bionic stable",
        ],
        check=False,
    )
    run(["sudo", "apt", "update"], check=False)
    run(
        [
            "sudo",
            "apt",
            "install",
            "-y",
            "docker-ce",
            "docker-ce-cli",
            "containerd.io",
        ],
        check=False,
    )

run(["sudo", "systemctl", "start", "docker"], check=False)
run(["sudo", "systemctl", "enable", "docker"], check=False)
run(["sudo", "usermod", "-aG", "docker", current_username()], check=False)
