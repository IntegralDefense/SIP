#!/bin/sh

while ! mysqladmin ping -h"db" -P"3306" --silent; do
    echo "Waiting for MySQL to be up..."
    sleep 1
done

exec gunicorn -b 0.0.0.0:5002 manage:app
