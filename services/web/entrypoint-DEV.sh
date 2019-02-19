#!/bin/sh

while ! mysqladmin ping -h"db" -P"3306" --silent; do
    echo "Waiting for MySQL to be up..."
    sleep 1
done

exec flask run --host=0.0.0.0 --port 5001
