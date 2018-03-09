from setuptools import setup, find_packages

setup(
    author='rr-',
    author_email='rr-@sakuya.pl',
    name='booru-toolkit',
    long_description='Various *booru tools',
    packages=find_packages(),

    entry_points={
        'console_scripts': [
            'dl-booru = booru_toolkit.download.__main__:main',
            'ul-booru = booru_toolkit.upload.__main__:main'
        ]
    },

    install_requires=[
        'aioconsole',
        'configargparse',
        'requests',
        'bs4',
        'urwid',
        'urwid-readline',
        'sqlalchemy',
    ])
