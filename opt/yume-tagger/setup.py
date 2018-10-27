from setuptools import setup, find_packages

setup(
    author='rr-',
    author_email='rr-@sakuya.pl',
    name='yume-tagger',
    long_description='Yume.pl tag manager',
    packages=find_packages(),
    entry_points={
        'console_scripts': ['yume-tagger = yume_tagger.__main__:main']
    },
    install_requires=[
        'configargparse',
        'requests',
        'tabulate',
        'wcwidth',
        'filelock',
    ],
)
