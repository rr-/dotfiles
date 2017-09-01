from setuptools import setup, find_packages


setup(
    author='rr-',
    author_email='rr-@sakuya.pl',
    name='panel',
    long_description='lemonbar on heavy steroids',
    packages=find_packages(),
    entry_points={'console_scripts': ['panel = panel.__main__:main']},
    package_dir={'panel': 'panel'},
    package_data={'panel': ['data/**/*']},
    install_requires=[
        'PyQT5',
        'python-xlib',
        'psutil',
    ], extras_require={
        'alsa': ['pyalsaaudio'],
    })
