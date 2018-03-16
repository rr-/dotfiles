from setuptools import setup, find_packages

setup(
    author='rr-',
    author_email='rr-@sakuya.pl',
    name='edict',
    long_description='EDICT lookup tool',
    packages=find_packages(),
    entry_points={'console_scripts': ['edict = edict.__main__:main']},
    install_requires=['requests', 'sqlalchemy', 'xdg'])
