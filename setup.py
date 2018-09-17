#!/usr/bin/python

import os

from setuptools import setup, find_packages

this_dir = os.path.dirname(os.path.abspath(__file__))

readme_path = os.path.join(this_dir, 'README.rst')

with open(readme_path) as f:
    long_description = f.read()

# Read the requirements from the filesystem
req_file = os.path.join(this_dir, 'requirements.d', 'all.txt')
with open(req_file) as f:
    install_requires = f.read().splitlines()

try:
    import importlib
except ImportError:
    install_requires.append('importlib')

setup(
    name='bepasty',
    version='0.5.0',
    license='BSD 2-clause',
    author='The Bepasty Team (see AUTHORS file)',
    author_email='',
    maintainer='Thomas Waldmann',
    maintainer_email='tw@waldmann-edv.de',
    description='a binary pastebin / file upload service',
    long_description=long_description,
    url='http://github.com/bepasty/bepasty-server/',
    keywords="text image audio video binary pastebin upload download service wsgi flask",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    package_data={
        'bepasty': [
            'src/static/app/css/*.css',
            'src/static/app/js/*.js',
            'src/templates/*',
        ],
    },
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'bepasty-server = bepasty.cli.server:main',
            'bepasty-object = bepasty.cli.object:main',
        ],
    },
    install_requires=install_requires,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
