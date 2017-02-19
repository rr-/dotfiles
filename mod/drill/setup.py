from setuptools import setup, find_packages

setup(
    name='drill',
    version='1.2.0',
    long_description=__doc__,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'drill = drill.__main__:main'
        ]
    },
    install_requires=[
        'python-dateutil',
        'sqlalchemy',
        'jinja2',
    ],
    package_dir={'drill': 'drill'},
    package_data={'drill': ['data/*.*']},
)
