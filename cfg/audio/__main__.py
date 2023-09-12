from libdotfiles.packages import try_install
from libdotfiles.util import HOME_DIR, PKG_DIR, copy_file, create_symlink, run

try_install("alsa-utils")
try_install("pulseaudio")
try_install("pulseaudio-bluetooth")
try_install("pavucontrol")

copy_file(
    PKG_DIR / "audio-sources.yml", HOME_DIR / ".config/audio-sources.yml"
)
create_symlink(
    PKG_DIR / "cycle-audio-device", HOME_DIR / ".local/bin/cycle-audio-device"
)

run(["pulseaudio", "-D"])
