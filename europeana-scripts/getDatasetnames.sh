#!/bin/bash

URL=`echo $1 | jq .url | cut -d "\"" -f 2`
ID=`echo $1 | jq .id | cut -d "\"" -f 2`

mkdir $ID
cd $ID

CURSOR=*

while [ "$CURSOR" != "null" ]
do
    URL2=${URL/"\$CURSOR"/$CURSOR}
    echo $URL2
    curl $URL2 -o "output.json.tmp"

#    echo "$CURSOR"

    for i in `seq 1 100`
    do
        cat output.json.tmp | jq .items[$i].edmDatasetName[0] | cut -d "\"" -f 2 >> datasetnames.txt
    done

    CURSOR=`cat output.json.tmp | jq .nextCursor | cut -d "\"" -f 2`
done

sort -u -o datasetnames.txt datasetnames.txt 

rm -f output.json.tmp
