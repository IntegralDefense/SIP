# SIP: Simple Intel Platform

TODO: Proper documentation. :-)

Run the included setup script to begin configuration.

```
./setup.py
```

The setup script will walk you through:
* Creating dev/test/production Docker environments
* Setting the MySQL root user password
* Creating a non-root MySQL user and password
* Creating an optional self-signed HTTPS certificate

Once you answer the setup script's questions, it will generate files containing the environment variables for the MySQL and Flask Docker containers.

If you created a dev or a production environment, their containers will be built and initialized with the default database values specified in the setup.ini file:

```
services/web/etc/setup.ini
```

## To run the unit/integration tests:

NOTE: A separate test Docker environment will be automatically built if you chose to build either a dev or production environment.

```
bin/test.sh
```

## To initialize DB migrations (Flask-Migrate):

Note: This should only be performed for the DEV environment.

```
bin/db-init-DEV.sh
```

## To generate DB migrations (Flask-Migrate):

Note: This should only be performed for the DEV environment.

```
bin/db-migrate-DEV.sh
```

## To upgrade the DB (Flask-Migrate):

Note: This can be performed on either the DEV or PROD environment.

```
bin/db-upgrade-DEV.sh
bin/db-upgrade-PROD.sh
```

## To enter a shell into one of the docker containers:

```
docker exec -i -t sip_web-dev_1 /bin/sh
docker exec -i -t <container_name> /bin/sh
```
