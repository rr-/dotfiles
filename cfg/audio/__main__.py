from libdotfiles.packages import try_install
from libdotfiles.util import run

try_install("alsa-utils")
try_install("pulseaudio")
try_install("pulseaudio-bluetooth")
try_install("pavucontrol")

run(["pulseaudio", "-D"])
