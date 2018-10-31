from setuptools import find_packages, setup

setup(
    author="rr-",
    author_email="rr-@sakuya.pl",
    name="crawl",
    long_description="Dumb regex-based downloader",
    packages=find_packages(),
    entry_points={"console_scripts": ["crawl = crawl.__main__:main"]},
    install_requires=["requests"],
)
