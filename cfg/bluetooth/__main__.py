from libdotfiles.packages import try_install
from libdotfiles.util import PKG_DIR, run

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

# USB autosuspend makes the MT7922 drop and lag HID devices
run(["sudo", "cp", PKG_DIR / "btusb.conf", "/etc/modprobe.d/btusb.conf"])
