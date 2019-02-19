#!/bin/bash

# Error if the events.json path does not exist
if [[ ! -f "$1" ]]
then
    echo "Could not find ACE events CSV: $1"
    exit 1
fi

# Error if the ACE alert base URL was not specified.
# https://youraceserver/saq/analysis?direct=
if [[ -z "$2" ]]
then
    echo "You must specify the ACE alert base URL"
    exit 1
fi

# Create the import directory if it does not exist
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
import_dir="$DIR/../services/web/import"
if [[ ! -d "$import_dir" ]]
then
    mkdir "$import_dir"
fi

# Copy the ace_events.csv file into the import directory
cp "$1" "$import_dir/ace_events.csv"

docker-compose -f docker-compose-DEV.yml build
docker-compose -f docker-compose-DEV.yml run web-dev pypy3 manage.py import-ace-events --baseurl="$2"

# Delete the events.json file from the container.
rm "$import_dir/ace_events.csv"