from libdotfiles.packages import try_install
from libdotfiles.util import distro_name

if distro_name() == "arch":
    try_install("python-pyqt5")
    try_install("ffms2-git")
    try_install("fftw")
elif distro_name() == "linuxmint":
    try_install("python3-setuptools")
    try_install("python3-pip")
    try_install("wheel", method="pip")
    try_install("python3-dev")
    try_install("python3-pyqt5")
    try_install("libffms2-4")
    try_install("libfftw3-bin")
    try_install("libmpv-dev")
    try_install("libass-dev")
