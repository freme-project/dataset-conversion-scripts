package org.aksw.freme.orcid;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.UnsupportedEncodingException;
import java.net.URLEncoder;
import java.text.DecimalFormat;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.Map;
import java.util.Set;
import org.apache.commons.lang3.StringEscapeUtils;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

public class OrcidConverter {

	private String resourceTriples = "";
	private String baseUri = "http://orcid.org/"; 
	private Map<String, String[]> countryData = null;
	private Set<String> workIds = new HashSet<String>();
	
	public OrcidConverter(String countryFile) {
		countryData = readCountryData(countryFile);
	}
	
	private Map<String, String[]> readCountryData(String fileName) {
		Map<String, String[]> countryData = new HashMap<String, String[]>();
		try {
			BufferedReader br = new BufferedReader(new FileReader(fileName));
			String line = null;
			while((line = br.readLine()) != null) {
				String code = line.substring(1,3);
				String id = line.substring(line.lastIndexOf(",")+2,line.length()-1);
				String name = line.substring(6,line.lastIndexOf(",")-1);
				countryData.put(code, new String[]{id, name});
			}
			br.close();
			return countryData;
		} catch (FileNotFoundException e) {	
			System.out.println("File not found "+fileName);
		} catch (IOException e) {
			System.out.println("Can not read "+fileName);
		}
		return null;
	}
	
	public String convertOrcidJSON(File jsonFile) throws JsonProcessingException, IOException {
		ObjectMapper m = new ObjectMapper();
		JsonNode rootNode = m.readTree(jsonFile);
		JsonNode profNode = rootNode.path("orcid-profile");
		JsonNode idNode = profNode.path("orcid-identifier");
		String uri = convertIdentifierNode(idNode);
		JsonNode bioNode = profNode.path("orcid-bio");
		convertBioNode(bioNode, uri);
		convertContact(bioNode, uri);
		JsonNode works = profNode.findPath("orcid-work");
		convertWorks(works, uri);
		return resourceTriples;
	}
	
	private void convertWorks(JsonNode works, String uri) {
	
		for(int i = 0; i<works.size(); i++) {
			JsonNode work = works.get(i);
		//check if put codes are unique
			String workId = work.get("put-code").asText();
			if(this.workIds.contains(workId)) {
				System.err.println("DUPLICATE PUT CODE "+uri);
			} else {
				this.workIds.add(workId);
			}
			resourceTriples += "<http://orcid.org/work/"+workId+"> <http://purl.org/dc/terms/creator> <"+uri+"> .\n";

			try {
				convertWork(work, "http://orcid.org/work/"+workId);
			} catch(NullPointerException n) {
				System.out.println(uri);
				n.printStackTrace();
			}
		}		
	}

	private void convertWork(JsonNode work, String uri) {
		
		//title
		if(!work.get("work-title").isNull()) {
			resourceTriples += "<"+uri+"> "
					+ "<http://purl.org/dc/terms/title> "
					+ "\""+cleanText(work.get("work-title").get("title").get("value").asText().trim())+"\" .\n";
		}
		
		//citation
		if(!work.path("work-citation").isMissingNode()&&
				!work.path("work-citation").isNull()) {
			
			JsonNode citation = work.path("work-citation");
			String citationText = cleanText(citation.get("citation").asText());
			resourceTriples += "<"+uri+"> "
					+ "<http://orcid.org/ns#citation/"+citation.get("work-citation-type").asText().toLowerCase()+"> "
					+ "\""+citationText+"\" .\n";	
		}	
		resourceTriples += "<"+uri+"> "
				+ "<http://www.w3.org/1999/02/22-rdf-syntax-ns#type> "
				+ "<"+getWorkType(work.get("work-type").asText())+"> .\n";
		
		//date
		if(!work.path("publication-date").path("year").isMissingNode()&&
				!work.path("publication-date").path("year").isNull()) {
			
			resourceTriples += "<"+uri+"> "
					+ "<http://purl.org/dc/terms/issued> "
					+ "\""+work.path("publication-date").path("year").get("value").asText()+"\" .\n";
		}
		
		//external id
		if(!work.findPath("work-external-identifier").isMissingNode()&&
				!work.findPath("work-external-identifier").isNull()) {
			
			JsonNode workExternalIds = work.findPath("work-external-identifier");
			for(int i = 0; i<workExternalIds.size();i++) {
				JsonNode workExternalId = workExternalIds.get(i);
				
				resourceTriples += "<"+uri+"> "
						+ "<"+getWorkIDType(workExternalId.get("work-external-identifier-type").asText().toLowerCase())+"> "
						+ "\""+ cleanText(workExternalId.get("work-external-identifier-id").get("value").asText())  +"\" .\n";
			}
		}
		
		//journal
		if(!work.findPath("journal-title").isMissingNode()&&
				!work.findPath("journal-title").isNull()) {
			String journalName = cleanText(work.findPath("journal-title").get("value").asText());
			String journalUri = "";
			try {
				journalUri = "http://orcid.org/collection/"+URLEncoder.encode(journalName,"UTF-8");
			} catch (UnsupportedEncodingException e) {
			//this doesn't happen
				e.printStackTrace();
			}
			if(!journalUri.isEmpty()) {
				resourceTriples += "<"+uri+"> <http://purl.org/dc/terms/isPartOf> <"+journalUri+"> .\n";
				resourceTriples += "<"+journalUri+"> <http://purl.org/dc/terms/title> \""+journalName+"\" .\n";
				if(!work.path("publication-date").path("year").isMissingNode()&&
						!work.path("publication-date").path("year").isNull()) {
					
					resourceTriples += "<"+journalUri+"> "
							+ "<http://purl.org/dc/terms/issued> "
							+ "\""+work.path("publication-date").path("year").get("value").asText()+"\" .\n";
				}
			}
				
		}
		
		//co authors
		if(!work.findPath("work-contributors").isMissingNode()&&
				!work.findPath("work-contributors").isNull()) {
			
			JsonNode workContributors = work.findPath("work-contributors").path("contributor");
			for(int i = 0; i<workContributors.size();i++) {
				JsonNode workContributor = workContributors.get(i);
				
				if(!workContributor.path("contributor-orcid").isNull()) {
					resourceTriples += "<"+uri+"> "
							+ "<http://purl.org/dc/terms/contributor> "
							+ "<http://orcid.org/"+workContributor.path("contributor-orcid").get("value").asText()+"> .\n";
				} else if(!workContributor.path("credit-name").isNull()) {
					resourceTriples += "<"+uri+"> "
							+ "<http://orcid.org/ns#contributor> \""+cleanText(workContributor.path("credit-name").get("value").asText())+"\" .\n";
				}
			}
		}
	}
	
	private String cleanText(String text) {
		return StringEscapeUtils.escapeJava(text.trim()
					.replace("\n"," ")
					.replace("\t", " "));
	}

	private String convertIdentifierNode(JsonNode idNode) {
		String uri = baseUri+idNode.get("path").asText();
		resourceTriples += "<"+uri+"> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://xmlns.com/foaf/0.1/Person> .\n";
		resourceTriples += "<"+uri+"> <http://purl.org/dc/terms/identifier> \""+idNode.get("path").asText()+"\" .\n";
		return uri;
	}
	
	private void convertBioNode(JsonNode bioNode, String uri) {
		JsonNode details = bioNode.path("personal-details");
		String name = cleanText(details.path("given-names").path("value").asText())+" "+cleanText(details.path("family-name").path("value").asText());
		resourceTriples += "<"+uri+"> <http://www.w3.org/2000/01/rdf-schema#label> \""+name+"\" .\n";
		
		JsonNode creditName = details.path("credit-name");
		if(!creditName.isMissingNode()&&!creditName.isNull()) {
			resourceTriples += "<"+uri+"> <http://xmlns.com/foaf/0.1/name> \""+cleanText(creditName.path("value").asText())+"\" .\n";
		}
		
		JsonNode otherName = details.path("other-names").path("other-name");
		if(otherName.size()>0) {
			String[] names = otherName.get(0).path("value").asText().split(",");	
			for(String other : names) {
				resourceTriples += "<"+uri+"> <http://orcid.org/ns#otherName> \""+cleanText(other)+"\" .\n";
			}
		}
		
		JsonNode urls = bioNode.path("researcher-urls").path("researcher-url");
		if(urls.size()>0) {
			for(int i = 0; i<urls.size();i++) {
				String url = urls.get(i).path("url").path("value").asText();
				String urlProp = getUrlProp(url);
				resourceTriples += "<"+uri+"> <"+urlProp+"> <"+url.trim()+"> .\n";
			}
		}
		
		JsonNode biography = bioNode.path("biography");
		if(!biography.path("value").asText().isEmpty()) {
			resourceTriples += "<"+uri+"> <http://purl.org/vocab/bio/0.1/biography> \""+cleanText(biography.path("value").asText())+"\" .\n";
		}
		
		JsonNode externalIds = bioNode.path("external-identifiers").path("external-identifier");
		if(externalIds.size()>0) {
			for(int i = 0; i<externalIds.size();i++) {
				String externalId = externalIds.get(i).path("external-id-url").path("value").asText();
				resourceTriples += "<"+uri+"> <http://www.w3.org/2002/07/owl#sameAs> <"+externalId.trim()+"> .\n";
			}
		}
		
	}
	
	private String getUrlProp(String url) {
		if(url.contains("linkedin.com")) 
			return "http://orcid.org/ns#linkedIn";
		else if(url.contains("scholar.google.com"))
			return "http://orcid.org/ns#googleScholar";
		else if(url.contains("twitter.com"))
			return "http://orcid.org/ns#twitter";
		else if(url.contains("facebook.com"))
			return "http://orcid.org/ns#facebook";
		else if(url.contains("google.com/+"))
			return "http://orcid.org/ns#googlePlus";
		else if(url.contains("youtube.com"))
			return "http://orcid.org/ns#youtube";
		else
			return "http://xmlns.com/foaf/0.1/homepage";
	}
	
	private String getWorkType(String orcidWorkType) {
		if(orcidWorkType.toLowerCase().contains("article")) 
			return "http://purl.org/ontology/bibo/Article";
		else if(orcidWorkType.toLowerCase().contains("book")&&!orcidWorkType.toLowerCase().contains("chapter"))
			return "http://purl.org/ontology/bibo/Book";
		else if(orcidWorkType.toLowerCase().contains("chapter"))
			return "http://purl.org/ontology/bibo/Chapter";
		else if(orcidWorkType.toLowerCase().contains("report"))
			return "http://purl.org/ontology/bibo/Report";
		else if(orcidWorkType.toLowerCase().contains("manual"))
			return "http://purl.org/ontology/bibo/Manual";
		else if(orcidWorkType.toLowerCase().contains("dissertation"))
			return "http://purl.org/ontology/bibo/Thesis";
		else
			return "http://purl.org/ontology/bibo/Document";
	}
	
	private String getWorkIDType(String workIDType) {
		if(workIDType.toLowerCase().equals("doi")) 
			return "http://purl.org/ontology/bibo/doi";
		else if(workIDType.toLowerCase().equals("issn"))
			return "http://purl.org/ontology/bibo/issn";
		else if(workIDType.toLowerCase().contains("isbn"))
			return "http://purl.org/ontology/bibo/isbn";
		else if(workIDType.toLowerCase().contains("lccn"))
			return "http://purl.org/ontology/bibo/lccn";
		else if(workIDType.toLowerCase().contains("oclc"))
			return "http://purl.org/ontology/bibo/oclcnum";
		else if(workIDType.toLowerCase().contains("pmid"))
			return "http://purl.org/ontology/bibo/pmid";
		else if(workIDType.toLowerCase().contains("uri"))
			return "http://purl.org/ontology/bibo/uri";
		else if(workIDType.toLowerCase().contains("asin"))
			return "http://purl.org/ontology/bibo/asin";
		else {
			return "http://orcid.org/ns#" + workIDType;
		}
			
	}

	private void convertContact(JsonNode bioNode, String uri) {
		JsonNode contact = bioNode.path("contact-details");
		if(!contact.isMissingNode()&&!contact.isNull()) {
			String countryCode = contact.path("address").path("country").path("value").asText();
			if(this.countryData.containsKey(countryCode)) {
				String[] country = this.countryData.get(countryCode);
				resourceTriples += "<"+uri+"> <http://schema.org/workLocation> <http://sws.geonames.org/"+country[0]+"> .\n";
				resourceTriples += "<http://sws.geonames.org/"+country[0]+"> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type>  <http://schema.org/Place> .\n";
				resourceTriples += "<http://sws.geonames.org/"+country[0]+"> <http://www.geonames.org/ontology#countryCode>  \""+countryCode+"\" .\n";
				resourceTriples += "<http://sws.geonames.org/"+country[0]+"> <http://www.w3.org/2000/01/rdf-schema#label>  \""+country[1]+"\" .\n";
			}
		}
		if(contact.path("email").size()>0) {
			resourceTriples += "<"+uri+"> <http://xmlns.com/foaf/0.1/mbox> \""+contact.path("email").get(0).path("value").asText()+"\" .\n";
		}
	}
	
	public void cleanResource() {
		resourceTriples = "";
	}
	
	public static void main(String[] args)  {
		String inputpath = args[0];
		System.out.println("Converting "+inputpath);
		OrcidConverter conv = new OrcidConverter(args[1]);
		try {
			File input = new File(inputpath);
			int count = 0;
			int total = 0;
			int fileNumber = 0;
			long tempTime = System.currentTimeMillis();
			float totalTime = 0;
			DecimalFormat df = new DecimalFormat("#,###,##0.00");
			String outfile = args[2];
			BufferedWriter dumpWriter = new BufferedWriter(new FileWriter(outfile+"0.nt", true));
			
			for(File jsonFile : input.listFiles()) {
				count ++;
				total ++;
				if(total%100==0) {
					tempTime = System.currentTimeMillis() - tempTime;
					totalTime += tempTime;
					System.out.println(total+" in "+df.format(totalTime/60000)+" (100 in "+(float)tempTime/100+" ms, "+ totalTime/total +" avg)");
					tempTime = System.currentTimeMillis();		
				}
					
				if(count>10000) {
					count = 0;
					fileNumber++;
					dumpWriter = new BufferedWriter(new FileWriter(outfile+fileNumber+".nt", true));
				}
				
				conv.convertOrcidJSON(jsonFile);				
				
				dumpWriter.append(conv.resourceTriples);
				dumpWriter.flush();
				conv.cleanResource();
			}
			dumpWriter.close();
			
		} catch (FileNotFoundException e) {
			System.out.println("File not found "+args[0]);
		} catch (IOException e) {
			System.out.println("Could not read "+args[0]);
			e.printStackTrace();
		}
	}
}