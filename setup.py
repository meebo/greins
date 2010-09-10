#!/usr/bin/env python

import os
from setuptools import setup, find_packages
from pkg_resources import Requirement, resource_filename

from greins import __version__

setup(
    name = 'greins',
    version = __version__,

    description = 'Greins is routing middleware for gunicorn',
    long_description = file(
        os.path.join(
            os.path.dirname(__file__),
            'README'
        )
    ).read(),
    author = 'Randall Leeds',
    author_email = 'randall@meebo-inc.com',

    zip_safe = False,
    packages = find_packages(exclude=['test']),
    include_package_data = True,

    install_requires = ['setuptools'],
	options = {'bdist_rpm':{	'post_install': 'post_install',
		   						'pre_uninstall': 'pre_uninstall'}}

)
