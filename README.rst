About
-----

Greins is a deployment and hosting tool which makes it easy to configure and
manage any number of WSGI_ apps in one Gunicorn_ server daemon.

Installation
------------

Greins requires a working version of Gunicorn_. It is recommended to read and
understand the Gunicorn_ installation instructions before using Greins.

Install from sources::

  $ python setup.py install

Or from PyPI::

  $ easy_install -U greins

Basic Usage
-----------

Greins installs one command line script invoked as ``greins``
