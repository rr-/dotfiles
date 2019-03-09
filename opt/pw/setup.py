from setuptools import find_packages, setup

setup(
    author="rr-",
    author_email="rr-@sakuya.pl",
    name="pw",
    long_description="poor man's keepassx",
    packages=find_packages(),
    entry_points={"console_scripts": ["pw = pw.__main__:main"]},
    package_dir={"pw": "pw"},
    install_requires=["pycryptodome"],
)
