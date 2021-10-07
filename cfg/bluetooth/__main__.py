from libdotfiles.packages import try_install
from libdotfiles.util import run

try_install("bluez")
try_install("bluez-utils")
try_install("blueman")

run(["sudo", "systemctl", "enable", "bluetooth"])
run(["sudo", "systemctl", "start", "bluetooth"])

run(
    [
        "sudo",
        "sh",
        "-c",
        'sed -i "s/#AutoEnable=false/AutoEnable=true/" /etc/bluetooth/main.conf',
    ]
)
