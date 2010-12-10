#!/usr/bin/env python

import os
from setuptools import setup, find_packages
from pkg_resources import Requirement, resource_filename

from greins import __version__

setup(
    name = 'greins',
    version = __version__,

    description = 'Greins is tack for Gunicorn.',
    long_description = file(
        os.path.join(
            os.path.dirname(__file__),
            'README.rst'
        )
    ).read(),
    author = 'Randall Leeds',
    author_email = 'randall@meebo-inc.com',
    url = 'http://github.com/meebo/greins',
    license = 'MIT License',

    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Internet',
        'Topic :: Utilities',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],

    zip_safe = False,
    packages = find_packages(exclude=['test']),
    include_package_data = True,

    install_requires = ['setuptools', 'gunicorn >= 0.11.0'],

    entry_points="""
    [console_scripts]
    greins=greins.app:run
    """
)
