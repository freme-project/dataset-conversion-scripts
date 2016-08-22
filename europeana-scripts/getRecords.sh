#!/usr/bin/env bash

DATASET=$1
FOLDER=$2

function process {
	URL=$1
	#download the records in xml format
	curl -o $FOLDER/output.xml.tmp --connect-timeout 300 --retry 10 $URL 
	sed ':a;N;$!ba;s/\n//g' $FOLDER/output.xml.tmp | sed 's:</record>:</record>\n:g' > $FOLDER/output.xml.tmp2
	mv $FOLDER/output.xml.tmp2 $FOLDER/output.xml.tmp
	#get token
        TOKEN=`tail -1 $FOLDER/output.xml.tmp | sed -n 's:.*<resumptionToken.*>\(.*\)</resumptionToken>.*:\1:p'`
	#echo $TOKEN
	#remove first and last line
	head -n -1 $FOLDER/output.xml.tmp | tail -n +2 > $FOLDER/output.xml.tmp2
	mv $FOLDER/output.xml.tmp2 $FOLDER/output.xml.tmp
	rm -f $FOLDER/output.xml.tmp2
	#get rdfxml of each record + convert to n-triples
 	./convert2ntriples.sh $FOLDER/output.xml.tmp $FOLDER	
	rm -f $FOLDER/output.xml.tmp
}

process "http://oai.europeana.eu/oaicat/OAIHandler?verb=ListRecords&from=&until=&set=$DATASET&metadataPrefix=edm"

while [ "$TOKEN" != "" ]
do
	process "http://oai.europeana.eu/oaicat/OAIHandler?verb=ListRecords&resumptionToken=$TOKEN"
done
