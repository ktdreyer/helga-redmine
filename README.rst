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

Optional: Authenticated access
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default, Helga only reads tickets that are publicly accessible. You may
optionally give Helga privilieged access to Redmine and allow Helga to read
private tickets by setting the ``REDMINE_API_KEY`` variable::

  REDMINE_API_KEY = "598bde2b1ee7082b5ead63712a9fc41dcc4ea160"

The Redmine software provides each user account with its own API key that looks
like a sha1 string. This string can be found by browsing to the "/my/account"
page in Redmine.

When ``REDMINE_API_KEY`` is set, Helga will be able to read private tickets
with using the permissions of the user to whom the API key belongs.

**Note**: This authentication feature can expose private information (ticket
subjects) about your Redmine bugs. If you use this feature, be sure that the
networks to which Helga connects are restricted. Everyone in Helga's channels
will see the private information, so the assumption is that they already have
rights to read the private tickets.
