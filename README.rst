A Redmine plugin for helga chat bot
===================================

About
-----

Helga is a Python chat bot. Full documentation can be found at
http://helga.readthedocs.org.

This Redmine plugin allows Helga to respond to Redmine ticket numbers in IRC
and print information about the tickets. For example::

  03:14 < ktdreyer> issue 8825
  03:14 < helgabot> ktdreyer might be talking about
                   http://tracker.ceph.com/issues/8825 [ceph-deploy tox tests
                   not working with python-remoto (CEPH_DEPLOY_NO_VENDOR)]

Installation
------------
This Redmine plugin is `available from PyPI
<https://pypi.python.org/pypi/helga-redmine>`_, so you can simply install it
with ``pip``::

  pip install helga-redmine

If you want to hack on the helga-redmine source code, in your virtualenv where
you are running Helga, clone a copy of this repository from GitHub and run
``python setup.py develop``.

Configuration
-------------
In your ``settings.py`` file (or whatever you pass to ``helga --settings``),
you must specify a ``REDMINE_URL``. For example::

  REDMINE_URL = "http://tracker.ceph.com/issues/%(ticket)s"

The ``%(ticket)s`` format string will be replaced with the ticket number.
