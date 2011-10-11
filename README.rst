About
-----

Greins is a Gunicorn_ application which makes it easy to configure and
manage any number of WSGI_ apps in one server daemon. It aims to simplify
the process of setting up any number of system-wide Gunicorn_ daemons.

Installation
------------

Greins requires a working version of Gunicorn_. It is recommended to read and
understand the Gunicorn_ installation instructions before using Greins.

Install from sources::

  $ python setup.py install

Install as an rpm::

  $ make rpm

Whatever was here before was wrong. There is no place in PyPI for Greins.
The most useful aspects of Greins are in the packaging, since it aims to
facilitate deployment of Gunicorn and adds no particular functionality itself.

There's an init script in etc/init aims to be LSB-compliant and packaging
for other distributions and systems is an ongoing effort.

Those wishing to deploy Greins for their own infrastructure are encouraged
to contribute to the development.

Basic Usage
-----------

Greins installs one command line script invoked as ``greins``.

greins
+++++++++

Options are the same as for Gunicorn_ with one exception: the single
APP_MODULE argument is replaced by APP_DIR, a directory containing python
source files as described in the following section.

Application Configuration
+++++++++++++++++++++++++

Applications should be configured by placing a python source file in the
configuration directory. This file should populate a dictionary in the global
scope called ``mounts`` which maps address prefixes (or 'mount points') to
WSGI handler functions.

These files are evaluated just like a Gunicorn_ `config file`_. Server hooks
are valid in these configuration files and work as in Gunicorn_. Other options,
such as logging and worker configuration, are ignored and should be configured
globally for the Greins application.

It should be possible to write an application for Gunicorn_ and then place
the application's configuration inside the configuration directory for Greins
to begin using it within Greins immediately.

Examples
++++++++

The examples directory runs a single ``greins`` application from the file
``test.py`` which demonstrates loading several routes as well as using the
``gunicorn`` server hooks. To run the examples, launch ``greins`` from the
directory above ``examples`` with:

  $ greins examples

The ``greins`` command accepts ``gunicorn`` options. For example:

  $ greins -kgevent -b0.0.0.0:8080 examples

LICENSE
-------

Greins is released under the MIT License. See the LICENSE_ file for more
details.

.. _Gunicorn: http://gunicorn.org/
.. _WSGI: http://wsgi.org/
.. _`config file`: http://gunicorn.org/configuration.html
.. _LICENSE: https://github.com/meebo/greins/blob/master/LICENSE
