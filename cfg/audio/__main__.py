from libdotfiles import packages, util

packages.try_install("alsa-utils")
packages.try_install("pulseaudio")
packages.try_install("pulseaudio-bluetooth")
packages.try_install("pavucontrol")

util.run(["pulseaudio", "-D"])
