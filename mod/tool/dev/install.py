import packages


def run():
    packages.try_install('make')
    packages.try_install('gcc')
    packages.try_install('automake')
    packages.try_install('lsof')
