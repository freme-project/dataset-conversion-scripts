# GRID conversion script 

This script converts the raw GRID dump to RDF.

To start the conversion run

`mvn exec:java -Dexec.mainClass="cz.ctu.fit.java.nif.test.suite.TestConvertGrid" -Dexec.args="-Xms4G -Xmx4G /Users/Milan/Desktop/grid/grid.json /Users/Milan/Desktop/grid/"`

The first parameter is the location of the JSON dump of the GRID dataset. You can download the latest dump from https://www.grid.ac/
The second parameter is the output location - where the RDF files will be placed.
