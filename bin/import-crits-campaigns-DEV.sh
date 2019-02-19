#!/bin/bash

# Error if the campaigns.json path does not exist
if [[ ! -f "$1" ]]
then
    echo "Could not find CRITS campaigns JSON: $1"
    exit 1
fi

# Create the import directory if it does not exist
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
import_dir="$DIR/../services/web/import"
if [[ ! -d "$import_dir" ]]
then
    mkdir "$import_dir"
fi

# Copy the campaigns.json file into the import directory
cp "$1" "$import_dir/campaigns.json"

docker-compose -f docker-compose-DEV.yml build
docker-compose -f docker-compose-DEV.yml run web-dev pypy3 manage.py import-crits-campaigns

# Delete the campaigns.json file from the container.
rm "$import_dir/campaigns.json"