#!/bin/bash

docker-compose -f docker-compose-PROD.yml build
docker-compose -f docker-compose-PROD.yml run --rm web-prod pypy3 manage.py db upgrade
docker-compose -f docker-compose-PROD.yml down