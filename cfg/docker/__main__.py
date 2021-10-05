import tempfile
from pathlib import Path

from libdotfiles.util import download, run

my_user = run(
    ["whoami"], check=True, capture_output=True, text=True
).stdout.strip()

with tempfile.TemporaryDirectory() as tmpdir:
    target_file = Path(tmpdir) / "docker-key.gpg"
    download("https://download.docker.com/linux/ubuntu/gpg", target_file)
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
run(["sudo", "usermod", "-aG", "docker", my_user], check=False)
