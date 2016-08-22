#!/bin/bash

FILE=$1
FOLDER=$2

while IFS='' read -r line || [[ -n "$line" ]]; do
#	echo $line
#   	echo `echo \'$line\' | sed -n 's/.*<rdf:RDF/<rdf:RDF/gp' | sed -n 's/<\/rdf:RDF>.*/<\/rdf:RDF>/gp'`
    	echo \'$line\' | sed -n 's/.*<rdf:RDF/<rdf:RDF/gp' | sed -n 's/<\/rdf:RDF>.*/<\/rdf:RDF>/gp' > $FOLDER/rdfxml.xml.tmp
    	rapper -wq $FOLDER/rdfxml.xml.tmp  >> $FOLDER/triples.nt.tmp
#    	exit
done < $FILE

sort -uS 1G $FOLDER/triples.nt.tmp | xz >> $FOLDER/triples.nt.xz

#remove temporary files
rm -f $FOLDER/triples.nt.tmp
rm -f $FOLDER/rdfxml.xml.tmp
