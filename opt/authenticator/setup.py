from setuptools import find_packages, setup

setup(
    author="rr-",
    author_email="dash@wind.garden",
    name="authenticator",
    long_description="CLI 2FA authenticator",
    packages=find_packages(),
    entry_points={
        "console_scripts": ["authenticator = authenticator.__main__:main"]
    },
    install_requires=["xdg", "python-dateutil", "cryptography"],
)
