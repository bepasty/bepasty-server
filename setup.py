#!/usr/bin/python

import os

from setuptools import setup, find_packages

from bepasty import (project, version, license, description,
                     author, author_email, maintainer, maintainer_email)

readme_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           'README.rst')
with open(readme_path) as f:
    long_description = f.read()

install_requires = [
    'flask>=0.10',
    'Pygments',
]

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
    keywords="text image audio video binary pastebin upload download service wsgi flask ceph",
    packages=find_packages(),
    package_data={
        'bepasty': [
            'static/app/css/*.css',
            'static/app/js/*.js',
            'static/bootbox/*.js',
            'static/bootstrap/fonts/*',
            'static/jquery.fileupload/css/*.css',
            'static/jquery.fileupload/img/*',
            'static/jquery.fileupload/js/*.js',
            'static/jquery.fileupload/js/vendor/*.js',
            'static/pygments/*.css',
            'templates/*',
        ],
    },
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': ['bepasty-server = bepasty.app:server_cli'],
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
