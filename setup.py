from confgen import __version__
from setuptools import setup, find_packages


def read_file(x):
    return [l.strip() for l in open(x).readlines()]

setup(
    name='confgen',
    version=__version__,
    packages=find_packages(),
    include_package_data=True,
    install_requires=read_file("requirements.txt"),
    entry_points={
        'console_scripts': ['confgen=confgen.cli:cli'],
    }
)
