#!/usr/bin/env python3

import os

from setuptools import setup, find_packages

this_dir = os.path.dirname(os.path.abspath(__file__))

readme_path = os.path.join(this_dir, 'README.rst')

with open(readme_path) as f:
    long_description = f.read()


setup(
    name='bepasty',
    use_scm_version={
        'write_to': 'src/bepasty/_version.py',
    },
    license='BSD 2-clause',
    author='The Bepasty Team (see AUTHORS file)',
    author_email='',
    maintainer='Thomas Waldmann',
    maintainer_email='tw@waldmann-edv.de',
    description='a binary pastebin / file upload service',
    long_description=long_description,
    url='https://github.com/bepasty/bepasty-server/',
    keywords="text image audio video binary pastebin upload download service wsgi flask",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'bepasty-server = bepasty.cli.server:main',
            'bepasty-object = bepasty.cli.object:main',
        ],
    },
    setup_requires=['setuptools_scm', ],
    install_requires=[
        'Flask',
        'Pygments',
        'xstatic',
        'XStatic-asciinema-player',
        'xstatic-bootbox>=5.4.0',
        'xstatic-bootstrap>=4.0.0.0,<5.0.0.0',
        'xstatic-font-awesome',
        'xstatic-jquery',
        'xstatic-jquery-ui',
        'xstatic-jquery-file-upload',
        'xstatic-pygments',
    ],
    extras_require={
        "magic": [
            'python-magic',
        ],
    },
    python_requires=">=3.5",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
