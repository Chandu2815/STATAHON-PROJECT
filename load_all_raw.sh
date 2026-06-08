#!/bin/bash

for f in /tmp/economic_census_1990/*.txt
do
    echo "Loading $f"

    sudo -u postgres psql -d statahon_db -c "\copy economic_census.enterprises_raw(record_text) FROM '$f';"
done
