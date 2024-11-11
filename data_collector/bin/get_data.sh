#!/bin/bash

source data_collector/conf/collector.conf

echo "Getting data from API: belib-points-de-recharge-pour-vehicules-electriques"
echo "Target path is set as: ${TARGET_PATH}"

curl -X 'GET' \
'https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/belib-points-de-recharge-pour-vehicules-electriques-donnees-statiques/exports/csv?limit=-1&offset=0&lang=fr&timezone=UTC' \
    -H 'accept: */*' > ${TARGET_PATH}/raw_data.csv