# ORCID conversion script 

This script converts the raw ORCID dump to RDF. The script was designed for the ORCID 2014 dump.

To convert ORCID to RDF you need to:
- download the ORCID dump from https://orcid.org/content/download-file
- unpack it
- execute:

`mvn exec:java -Dexec.mainClass="org.aksw.freme.orcid.OrcidConverter" -Dexec.args="-Xms4G -Xmx4G /PATH/TO/YOUR/INPUT/FILES /PATH/TO/countries.csv"`
- execute postprocess.sh
