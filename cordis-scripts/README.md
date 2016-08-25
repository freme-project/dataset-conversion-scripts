# How to use

This python script is used to extract data from a CORDIS dataset. 

## Prepare the data

There is a crucial problem with the CORDIS generic .csv file; It uses simple `,` and `"` for seperating different entries and marking multiline entries. The datasets however are filled with those symbols within the entries. Furthermore, there are multiple different languages being used within the dataset, often even very special characters. To avoid false parsing, the dataset needs to be manually prepared: 

1. Get the the CORDIS datasets in Excel form (most likely from [here](https://data.europa.eu/euodp/de/data/dataset/cordisfp7projects))
2. Export this dataset as a `.csv`
3. Set `ᛘ` (U+16D8) as the multiline indicator and `ᛥ` (U+16e5) as the entry seperator
4. Keep the filenames intact so `cordis` as well as `projects` or `organizations` is in it
5. Store the file in the same directory as the `csv2rdf.py` 

## Check for dependencies

Python 3 is being used, so make sure it is installed and the following dependencies are installed: 

* [iso3166](https://pypi.python.org/pypi/iso3166/0.6) - Used for the alpha 2 and alpha 3 countrycodes
* [rdflib](https://github.com/RDFLib/rdflib) - Used for creating and handling RDF data

## Running the scrip

If everything is in place simply execute `csv2rdf.py`, a prompt will show up with `Name of .csv file:` simply enter the full filename of the file (e.g. `cordis_projects.csv`). And the script should run everything else on its own.
