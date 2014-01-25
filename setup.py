#!/usr/bin/python

from setuptools import setup, find_packages

setup(
    name='bepasty',
    version='dev',
    packages=find_packages(),
    package_data={
        'bepasty': [
            'static/app/css/*.css',
            'static/app/js/*.js',
            'static/bootstrap/fonts/*',
            'static/jquery.fileupload/css/*.css',
            'static/jquery.fileupload/img/*',
            'static/jquery.fileupload/js/*.js',
            'static/jquery.fileupload/js/vendor/*.js',
            'templates/*',
        ],
    },
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask>=0.10',
        'Pygments',
    ],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
)
