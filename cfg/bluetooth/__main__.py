from libdotfiles import packages, util

packages.try_install("bluez")
packages.try_install("bluez-utils")
packages.try_install("blueman")

util.run(["sudo", "systemctl", "enable", "bluetooth"])
util.run(["sudo", "systemctl", "start", "bluetooth"])

util.run(
    [
        "sudo",
        "sh",
        "-c",
        'sed -i "s/#AutoEnable=false/AutoEnable=true/" /etc/bluetooth/main.conf',
    ]
)
