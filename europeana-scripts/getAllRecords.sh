#!/usr/bin/env bash

FOLDER=$1

while IFS='' read -r line || [[ -n "$line" ]]; do
    ./getRecords.sh $line $FOLDER
done < $FOLDER/datasetnames.txt

xzcat $FOLDER/triples.nt.xz | sort -uS 2G | xz > $FOLDER/uniq_triples.nt.xz
