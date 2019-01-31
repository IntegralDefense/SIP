#!/bin/bash

docker-compose -f docker-compose-DEV.yml run --rm web-dev pypy3 manage.py db migrate
docker-compose -f docker-compose-DEV.yml down