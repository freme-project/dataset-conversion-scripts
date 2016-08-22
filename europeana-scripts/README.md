# Scripts
## getDatasetNames.sh
This script gets all the names of the datasets that belong to the collections (represented by their URLs in `collection_urls.txt`).
The names are stored in `datasetnames.txt`.

## getAllRecords.sh
This script downloads all the records for each dataset in `datasetnames.txt` and converts them to `n-triples`.
It uses the scripts `getRecords.sh` and `convert2ntriples.sh`.

## convert2ntriples.sh
This script converts the the downloaded results (in `rdf/xml`) to `n-triples`.

## getRecords.sh
This script downloads a given dataset and stores the records in a given folder.

# Requirements
- [curl](https://curl.haxx.se/)
- [jq](https://stedolan.github.io/jq/)
- [rapper](http://librdf.org/raptor/rapper.html)

# Usage

1) create `collection_urls.txt` (an example can be found in `collection_urls_example.txt`)
2) execute `./getDatasetNames.sh`
3) execute `./getAllRecords.sh DATASET_NUMBER` (based on `datasetnames.txt`), or `parallel --progress ./getAllRecords.sh {} ::: `seq 1 1 TOTAL_NUMBER_OF_DATASETS``

