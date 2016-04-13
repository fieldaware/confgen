from setuptools import setup, find_packages
read_file = lambda x: [l.strip() for l in open(x).readlines()]

setup(
    name='confgen',
    version='0.1.0',
    packages=find_packages(),
    scripts=["bin/confgen"],
    install_requires=read_file("requirements.txt"),
)
