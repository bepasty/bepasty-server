#!/usr/bin/python

import os

from setuptools import setup, find_packages

from bepasty import (project, version, license, description,
                     author, author_email, maintainer, maintainer_email)

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
    name=project,
    version=version,
    license=license,
    author=author,
    author_email=author_email,
    maintainer=maintainer,
    maintainer_email=maintainer_email,
    description=description,
    long_description=long_description,
    url='http://github.com/bepasty/bepasty-server/',
    keywords="text image audio video binary pastebin upload download service wsgi flask",
    packages=find_packages(),
    package_data={
        'bepasty': [
            'static/app/css/*.css',
            'static/app/js/*.js',
            'templates/*',
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
        'Programming Language :: Python :: 2.6',
    ],
)
