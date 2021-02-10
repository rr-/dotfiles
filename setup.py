from setuptools import find_packages, setup

setup(
    author="rr-",
    author_email="rr-@sakuya.pl",
    name="libdotfiles",
    long_description="wrapper script around my dotfiles",
    packages=find_packages(),
    entry_points={"console_scripts": ["dotfiles = dotfiles.__main__:main"]},
    install_requires=["click", "coloredlogs"],
)
