#!/bin/sh

echo 'Waiting for PostgreSQL...'

while ! nc -z db 5432; do
	sleep 1
done

echo 'PostgreSQL started'

gunicorn -b 0.0.0.0:5000 manage:app
