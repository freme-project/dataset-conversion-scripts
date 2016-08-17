
package cz.ctu.fit.java.nif.test.suite;

import com.hp.hpl.jena.rdf.model.Model;
import com.hp.hpl.jena.rdf.model.ModelFactory;
import com.hp.hpl.jena.rdf.model.Property;
import com.hp.hpl.jena.rdf.model.Resource;
import com.hp.hpl.jena.sparql.vocabulary.FOAF;
import com.hp.hpl.jena.vocabulary.DC_11;
import com.hp.hpl.jena.vocabulary.RDFS;
import com.hp.hpl.jena.vocabulary.XSD;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.Iterator;
import java.util.logging.Level;
import java.util.logging.Logger;
import org.json.simple.JSONArray;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;

/**
 *
 * @author Milan Dojchinovski <milan.dojchinovski@fit.cvut.cz>
 * http://dojchinovski.mk
 */
public class GridConverter {
    public void convert(String dataLocation, String outputLocation) {
        System.out.println("Started loading the dataset...");
        try {
            int addressesCounter = 0;
            int relationshipCounter = 0;
            Model model = ModelFactory.createDefaultModel();
            model.setNsPrefix( "dc", DC_11.NS );
            model.setNsPrefix( "vcard", "http://www.w3.org/2006/vcard/ns#" );
            model.setNsPrefix( "dbp", "http://dbpedia.org/property/" );
            model.setNsPrefix( "dbo", "http://dbpedia.org/ontology/" );
            model.setNsPrefix( "rdfs", "http://www.w3.org/2000/01/rdf-schema#" );
            model.setNsPrefix( "frp", "http://www.freme-project.eu/ns/" );
            model.setNsPrefix( "geo", "http://www.w3.org/2003/01/geo/wgs84_pos#" );
            model.setNsPrefix( "foaf", FOAF.getURI() );
            model.setNsPrefix( "skos", "http://www.w3.org/2004/02/skos/core#" );
            model.setNsPrefix( "xsd", XSD.getURI() );
            
            JSONParser parser = new JSONParser();
            Object obj = parser.parse(new FileReader(dataLocation));
//            Object obj = parser.parse(new FileReader("/Users/Milan/Desktop/grid/grid.json"));
 
            JSONObject jsonObject = (JSONObject) obj;
            System.out.println("Loaded.");
            
            
//            String name = (String) jsonObject.get("Name");
//            String author = (String) jsonObject.get("Author");
            JSONArray institutes = (JSONArray) jsonObject.get("institutes");
            
// 
//            System.out.println("Name: " + name);
//            System.out.println("Author: " + author);
//            System.out.println("\nCompany List:");
            Iterator<JSONObject> iterator = institutes.iterator();
            while (iterator.hasNext()) {
                
                JSONObject instObj = iterator.next();
                
                String id = (String)instObj.get("id");
                String status = (String)instObj.get("status");

                if(status.equals("active")) {
                    
                    Resource instRes = model.createResource("http://www.freme-project.eu/resource/grid/institutes/"+id);
                    System.out.println(instRes);
                    
                    String name = (String)instObj.get("name");
                    instRes.addLiteral(RDFS.label, name);
                    
                    if(instObj.get("wikipedia_url") != null) {
                        if(!instObj.get("wikipedia_url").equals("")){
                            String wikiUrl = instObj.get("wikipedia_url").toString();
                            instRes.addProperty(FOAF.primaryTopic, model.createResource(wikiUrl.replaceAll(" ", "")));
                        }
                    }
                    
                    if(instObj.get("email_address") != null) {
                        if(!instObj.get("email_address").equals("")){
                            String email = instObj.get("email_address").toString();
                            instRes.addProperty(FOAF.mbox, model.createResource("mailto:"+email));
                        }
                    }
                    
                    // Links
                    JSONArray links = (JSONArray) instObj.get("links");
                    Iterator<String> linksIterator = links.iterator();
                    while(linksIterator.hasNext()) {
                        instRes.addProperty(FOAF.homepage, model.createResource(linksIterator.next().replaceAll(" ", "")));
                    }
                    
                    // acronyms
                    JSONArray acronyms = (JSONArray) instObj.get("acronyms");
                    Iterator<String> acronymsIterator = acronyms.iterator();
                    while(acronymsIterator.hasNext()) {
                        instRes.addProperty(model.createProperty("http://www.w3.org/2004/02/skos/core#altLabel"), acronymsIterator.next());
                    }

                    // aliases
                    JSONArray aliases = (JSONArray) instObj.get("aliases");
                    Iterator<String> aliasesIterator = aliases.iterator();
                    while(aliasesIterator.hasNext()) {
                        instRes.addProperty(model.createProperty("http://www.w3.org/2004/02/skos/core#altLabel"), aliasesIterator.next());
                    }
                    
                    // aliases
                    JSONArray types = (JSONArray) instObj.get("types");
                    Iterator<String> typesIterator = types.iterator();
                    while(typesIterator.hasNext()) {
                        instRes.addProperty(DC_11.subject, typesIterator.next());
                    }
                    
                    // ip_addresses
                    JSONArray ip_addresses = (JSONArray) instObj.get("ip_addresses");
                    Iterator<String> ip_addressesIterator = ip_addresses.iterator();
                    while(ip_addressesIterator.hasNext()) {
                        instRes.addProperty(model.createProperty("http://www.freme-project.eu/ns/ipaddress/"), ip_addressesIterator.next());
                    }
                    
                    // year established
                    if(instObj.get("established") != null) {
                        if(!instObj.get("established").equals("")){
                            String established = instObj.get("established").toString();
                            instRes.addProperty(model.createProperty("http://dbpedia.org/ontology/foundingYear"), established);
                        }
                    }
                    
                    // relationships
                    if(instObj.get("relationships") != null) {
                        JSONArray relationships = (JSONArray)instObj.get("relationships");
                        Iterator<JSONObject> relationshipsIterator = relationships.iterator();
                        while(relationshipsIterator.hasNext()) {
                            JSONObject relationship = relationshipsIterator.next();
                            String rel_type = relationship.get("type").toString();
                            String label = relationship.get("label").toString();
                            String affil_id = relationship.get("id").toString();
                            
                            Resource affiliationRes = model.createResource("http://www.freme-project.eu/resource/grid/relationships/"+relationshipCounter);
                            relationshipCounter++;
                            // TODO: the property should be checked again
                            instRes.addProperty(model.createProperty("http://www.freme-project.eu/ns/relationship"), affiliationRes);
                            
                            // TODO: the property should be checked again
                            affiliationRes.addProperty(model.createProperty("http://www.freme-project.eu/ns/relationType"), rel_type);

                            affiliationRes.addLiteral(RDFS.label, label);
                            affiliationRes.addProperty(DC_11.identifier, model.createResource("http://www.freme-project.eu/resource/grid/institutes/"+affil_id));
                        }
                    }

                    // external_ids
                    // currently only to types of ext. IDs are considered, ISNI and fundRef
                    if(instObj.get("external_ids") != null) {
                        JSONObject external_ids = (JSONObject)instObj.get("external_ids");
                        
                        // ISNI
                        if(external_ids.get("ISNI") != null) {
                            JSONArray isniArray = (JSONArray)external_ids.get("ISNI");
                            Iterator<String> isniIterator = isniArray.iterator();
                            while(isniIterator.hasNext()) {
                                String isniVal = isniIterator.next();
                                instRes.addLiteral(model.createProperty("http://dbpedia.org/ontology/isniId"), isniVal);
                            }
                        }
                        
                        // FundRef
                        if(external_ids.get("FundRef") != null) {
                            JSONArray fundRefArray = (JSONArray)external_ids.get("FundRef");
                            Iterator<String> fundRefIterator = fundRefArray.iterator();
                            while(fundRefIterator.hasNext()) {
                                String fundRefVal = fundRefIterator.next();
                                instRes.addLiteral(model.createProperty("http://www.freme-project.eu/ns/fundRef"), fundRefVal);
                            }
                        }
                    }
                    
                    // addresses
                    JSONArray addresses = (JSONArray) instObj.get("addresses");
                    Iterator<JSONObject> addressesIterator = addresses.iterator();
                    while(addressesIterator.hasNext()) {
                        JSONObject address = addressesIterator.next();
                        
                        Resource addressRes =  model.createResource("http://www.freme-project.eu/resource/grid/addresses/"+addressesCounter);
                        addressesCounter++;
                        instRes.addProperty(model.createProperty("http://www.w3.org/2006/vcard/ns#hasAddress"), addressRes);
                        
                        if(address.get("city") != null) {
                            if(!address.get("city").equals("")){
                                String city = address.get("city").toString();
                                addressRes.addProperty(model.createProperty("http://www.w3.org/2006/vcard/ns#locality"), city);
                            }
                        }
                        
                        if(address.get("state") != null) {
                            if(!address.get("state").equals("")){
                                String state = address.get("state").toString();
                                addressRes.addProperty(model.createProperty("http://www.w3.org/2006/vcard/ns#region"), state);
                            }
                        }
                        
                        if(address.get("country") != null) {
                            if(!address.get("country").equals("")){
                                String country = address.get("country").toString();
                                addressRes.addProperty(model.createProperty("http://www.w3.org/2006/vcard/ns#country-name"), country);
                            }
                        }
                        
                        if(address.get("country_code") != null) {
                            if(!address.get("country_code").equals("")){
                                String country_code = address.get("country_code").toString();
                                addressRes.addProperty(model.createProperty("http://dbpedia.org/property/iso31661Alpha"), country_code);
                            }
                        }
                        
                        if(address.get("state_code") != null) {
                            if(!address.get("state_code").equals("")){
                                String state_code = address.get("state_code").toString();
                                addressRes.addProperty(model.createProperty("http://dbpedia.org/property/provinceIsoCode"), state_code);
                            }
                        }
                        
                        if(address.get("postcode") != null) {
                            if(!address.get("postcode").equals("")){
                                String postcode = address.get("postcode").toString();
                                addressRes.addProperty(model.createProperty("http://dbpedia.org/property/zipCode"), postcode);
                            }
                        }
                        
                        if(address.get("line_1") != null) {
                            if(!address.get("line_1").equals("")){
                                String line_1 = address.get("line_1").toString();
                                System.out.println(line_1);
//                                addressRes.addProperty(model.createProperty("http://dbpedia.org/property/zipCode"), postcode);
                            }
                        }
                        
                        if(address.get("line_2") != null) {
                            if(!address.get("line_2").equals("")){
                                String line_2 = address.get("line_2").toString();
                                System.out.println(line_2);
//                                addressRes.addProperty(model.createProperty("http://dbpedia.org/property/zipCode"), postcode);
                            }
                        }
                        
                        if(address.get("line_3") != null) {
                            if(!address.get("line_3").equals("")){
                                String line_3 = address.get("line_3").toString();
                                System.out.println(line_3);
//                                addressRes.addProperty(model.createProperty("http://dbpedia.org/property/zipCode"), postcode);
                            }
                        }
                        
                        if(address.get("lat") != null) {
                            if(!address.get("lat").equals("")){
                                String lat = address.get("lat").toString();
                                addressRes.addProperty(model.createProperty("http://www.w3.org/2003/01/geo/wgs84_pos#lat"), lat);
                            }
                        }
                        
                        if(address.get("lng") != null) {
                            if(!address.get("lng").equals("")){
                                String lng = address.get("lng").toString();
                                addressRes.addProperty(model.createProperty("http://www.w3.org/2003/01/geo/wgs84_pos#long"), lng);
                            }
                        }
                        
                        // GeoNames link for the city
                        // TODO: following info is not converted:
                        // geonames_admin1, geonames_admin2, nuts_level1, nuts_level2, nuts_level3                        
                        if(address.get("geonames_city") != null) {
                            if(!address.get("geonames_city").equals("")){
                                JSONObject geonames_city = (JSONObject)address.get("geonames_city");
                                addressRes.addProperty(model.createProperty("http://www.w3.org/2006/vcard/ns#locality"), model.createResource("http://sws.geonames.org/"+geonames_city.get("id").toString()+"/"));
                            }
                        }
                    }
                }

//                System.out.println(iterator.next().toString());
            }
            String fileNameNT = outputLocation+"grid.nt";
            String fileNameTTL = outputLocation+"grid.ttl";
//            String fileNameNT = "/Users/Milan/Desktop/grid/grid.nt";
//            String fileNameTTL = "/Users/Milan/Desktop/grid/grid.ttl";
            FileWriter outNT = new FileWriter( fileNameNT );
            FileWriter outTTL = new FileWriter( fileNameTTL );
            try {
                model.write( outNT, "N-TRIPLES" );
                model.write( outTTL, "TTL" );
            }
            finally {
               try {
                   outNT.close();
                   outTTL.close();
               }
               catch (IOException closeException) {
                   // ignore
               }
            }

//            System.out.println(model);
            
            // TODOs
            // - addresses
            
            
        } catch (IOException ex) {
            Logger.getLogger(GridConverter.class.getName()).log(Level.SEVERE, null, ex);
        } catch (ParseException ex) {
            Logger.getLogger(GridConverter.class.getName()).log(Level.SEVERE, null, ex);
        }
    }
}
