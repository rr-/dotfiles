from dotinstall import packages, util


def run():
    if util.distro_name() == "arch":
        packages.try_install("python-pyqt5")
        packages.try_install("ffms2000-git")
        packages.try_install("fftw")
    elif util.distro_name() == "linuxmint":
        packages.try_install("python3-setuptools")
        packages.try_install("python3-pip")
        packages.try_install("wheel", method="pip")
        packages.try_install("python3-dev")
        packages.try_install("python3-pyqt5")
        packages.try_install("libffms2-4")
        packages.try_install("libfftw3-bin")
        packages.try_install("libmpv-dev")
        packages.try_install("libass-dev")
