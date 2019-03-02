Running SIP
***********

.. contents::
  :backlinks: none

After you have setup SIP with the included setup script, the following commands and scripts will help you to easily run and maintain SIP.

Integration Tests
-----------------

A separate TEST Docker environment will be automatically built if you chose to build either a DEV or PRODUCTION environment during the setup process.

::

   $ bin/test.sh

Database Migrations
-------------------

SIP uses `Flask-Migrate <https://flask-migrate.readthedocs.io/en/latest/>`_ to handle any database schema changes and migrations.

*NOTE*: This should only be performed for the DEV environment.

**Initialize**

This should never need to be performed unless you delete the included migrations directory. Additionally, it is only meant to run on the DEV environment.

::

   $ bin/db-init-DEV.sh

**Migrate**

Once you have made some changes to the database schema in the models.py file, you need to generate the schema migrations. This is also only meant to run on the DEV environment.

::

   $ bin/db-migrate-DEV.sh

**Upgrade**

After you have created the schema migrations (or have received migrations through a git pull), you need to upgrade your database. This can run on the DEV or PRODUCTION environments.

::

   $ bin/db-upgrade-DEV.sh
   $ bin/db-upgrade-PROD.sh

Debugging
---------

If SIP refuses to start, and you suspect the issue is with the Docker container itself, you can enter a shell to the containers:

::

   $ docker exec -i -t sip_web-dev_1 /bin/sh
   $ docker exec -i -t <container_name> /bin/sh