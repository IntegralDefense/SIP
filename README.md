# SIP: Simple Intel Platform

TODO: Proper documentation. :-)

For right now, the SUPER quick installation guide:

```
./setup.py
docker-compose up
docker-compose run web python manage.py setupdb
docker-compose run web python manage.py seeddb
```

## To run the unit/integration tests:

```
docker-compose run web python manage.py test
```

## To perform database schema migration/upgrades (via Flask-Migrate):

```
docker-compose run web python manage.py db migrate
docker-compose run web python manage.py db upgrade
```

## To enter a shell into one of the docker containers:

```
docker exec -i -t sip_web_1 /bin/sh
docker exec -i -t <container_name> /bin/sh
```
