from setuptools import setup, find_packages


setup(
    author='rr-',
    author_email='rr-@sakuya.pl',
    name='launcher',
    long_description='xdg-open replacement',
    packages=find_packages(),
    entry_points={'console_scripts': ['xdg-open = launcher.__main__:main']})
