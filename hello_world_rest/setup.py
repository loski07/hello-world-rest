from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Get python dependencies from the requirements file
with open(path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    install_requires = f.read()

setup(
    name='hello-world-rest',
    version='1.0',
    description='Program that exposes 2 REST endpoints to register your birthdate and greet you',
    long_description=long_description,

    url='https://github.com/loski07/hello-world-rest',
    author='Pablo Díaz <loski07@gmail.com>',

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Recruiting',
        'Programming Language :: Python :: 3.11'
    ],

    keywords='helloworld REST',

    packages=find_packages(exclude=['docs', 'tests']),

    install_requires=install_requires,

)
