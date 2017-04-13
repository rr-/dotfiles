from setuptools import setup, find_packages

setup(
    author='Marcin Kurczewski',
    author_email='rr-@sakuya.pl',
    name='booru-toolkit',
    long_description='Various *booru tools',
    packages=find_packages(),

    entry_points={
        'console_scripts': [
            'dl-booru = booru_toolkit.download:main',
            'ul-booru = booru_toolkit.upload:main'
        ]
    },

    install_requires=[
        'configargparse',
        'requests',
        'bs4',
        'urwid',
        'urwid-readline',
        'sqlalchemy',
    ])
