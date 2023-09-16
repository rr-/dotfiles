from libdotfiles.packages import try_install
from libdotfiles.util import PKG_DIR, run

try_install("iwd")
run(["sudo", "systemctl", "start", "systemd-resolved"])
run(["sudo", "systemctl", "enable", "systemd-resolved"])
run(["sudo", "cp", PKG_DIR / "iwd.conf", "/etc/iwd/main.conf"])
run(["sudo", "cp", PKG_DIR / "resolv.conf", "/etc/resolv.conf"])
