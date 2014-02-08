#!/usr/bin/python

from setuptools import setup, find_packages

with open('README.rst') as f:
    readme_content = f.read()

setup(
    name='bepasty',
    version='0.0.1',
    url='http://github.com/bepasty/bepasty-server/',
    license='BSD',
    author='The Bepasty Team (see AUTHORS)',
    description='A binary file upload service',
    long_description=readme_content,
    keywords="text image audio video binary pastebin upload service wsgi flask ceph",
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
    entry_points={
        'console_scripts': ['bepasty-server = bepasty:server_cli'],
    },
    install_requires=[
        'flask>=0.10',
        'Pygments',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
)
