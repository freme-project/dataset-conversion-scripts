#!/bin/bash

rapper -g sorted.nt -o turtle -f 'xmlns:dcterms="http://purl.org/dc/terms/"' -f 'xmlns:bibo="http://purl.org/ontology/bibo/"' -f 'xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"' -f 'xmlns:gn="http://www.geonames.org/ontology#"' -f 'xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"' -f 'xmlns:orcid="http://orcid.org/ns#"' -f 'xmlns:owl="http://www.w3.org/2002/07/owl#"' -f 'xmlns:bio="http://purl.org/vocab/bio/0.1/"' -f 'xmlns:schema="http://schema.org/"' -f 'xmlns:foaf="http://xmlns.com/foaf/0.1/"' > orcid_ex.ttl


