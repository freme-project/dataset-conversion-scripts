# -*- coding: utf-8 -*-
from iso3166 import countries
from datetime import date
from organization import Organization
from project import Project
from person import Person
from collections import namedtuple
from urllib import parse
from rdflib import Graph, URIRef, BNode, Literal, Namespace
from rdflib.namespace import RDF, FOAF, DC, XSD, DOAP, RDFS
import datetime

DBO = Namespace("http://dbpedia.org/ontology/")
CORDIS = Namespace("http://www.freme-project.eu/datasets/cordis/")
CORG = Namespace(CORDIS.organizations + "/")
CPRO = Namespace(CORDIS.projects + "/")
CPEO = Namespace(CORDIS.people + "/")
DBR = Namespace("http://dbpedia.org/resource/")

class Csv2Rdf:


    def __init__(self, filename):
        self.filename = filename

    def readInputFile(self):
        f = open(self.filename + '.csv', 'r', encoding="utf-8")
        text = []
        for line in f:
            text.append(line)
        f.close()
        return text

    def readTemplate(self, name):
        t = open(name, 'r', encoding="utf-8")
        text = []
        for line in t:
            text.append(line)
        t.close()
        return text

    def readTextInput(self, splitter):
        text = self.readInputFile()
        labels = []
        data = []
        for label in text[0].split(splitter, -2):
            if not '\n' in label:
                if '\ufeff' in label:
                    labels.append(label[1:])
                else:
                    labels.append(label)
        data.append(labels)
        for entry in text[1:]:
            lineData = []
            for value in entry.split(splitter, -2):
                if not '\n' in value:
                    lineData.append(value)
            data.append(lineData)
        return data

    def readMultilineInput(self, splitter):
        text = self.readInputFile()
        labels = []
        data = []
        for label in text[0].split(splitter):
            if '\n' != label:
                if '\ufeff' in label:
                    labels.append(label[1:])
                else:
                    labels.append(label)
        data.append(labels)
        toggle = False
        newLineData= True
        for entry in text[1:]:
            if newLineData:
                lineData = []
                newLineData = not newLineData
            for value in entry.split(splitter):
                if '"' in value or "'" in value:
                    value.replace('"','')
                    value.replace("'",'')
                if toggle:
                    lineData[-1] = lineData[-1] + value.replace('ᛘ','')
                else:
                    if value == '\n':
                        value = ''
                    lineData.append(value.replace('ᛘ',''))
                if 'ᛘ' in value:
                    toggle = not toggle
            if (len(data[0]) == len(lineData)):
                lineData[-1] = lineData[-1][:-1]
                data.append(lineData)
                newLineData = not newLineData
        return data

    def createOutput(self, data):
        template = self.readTemplate(self.filename + '_template.ttl')
        if self.filename == 'employment':
            for i, entry in enumerate(data[1:]):
                output = ('statbel:o' + str(i + 1) + ' a qb:Observation;\n\t' +
                          'qb:dataSet\tstatbel:dataset-employmentUnemployment;\n\t' +
                          'sdmx-dimension:refPeriod\t"' + self.transferQuartal(entry[0][-4:], entry[0][1]) + '"^^xsd:date;\n\t' +
                          'statbel:employed\t' + entry[3] + ';\n\t' +
                          'statbel:unemployed\t' + entry[1] + ';\n\t' +
                          'statbel:inactive\t' + entry[2] + ';\n\t.\n\n')
                template.append(output)
        elif self.filename == 'hpi':
            for i, entry in enumerate(data[1:]):
                output = ('statbel:o' + str(i + 1) + ' a qb:Observation;\n\t' +
                          'qb:dataSet\tstatbel:dataset-hpi;\n\t'
                          'sdmx-dimension:refPeriod\t"' + self.transferQuartal(entry[0][:4], entry[0][-1]) + '"^^xsd:date;\n\t' +
                          'statbel:inflation\t' + entry[1].replace(',','.') + ';\n\t.\n\n')
                template.append(output)
        elif self.filename == 'cordis_projects':
            for entry in data[1:]:
                template.append(self.createCordisProjects(entry))
        elif self.filename == 'cordis_organizations':
            for entry in data[1:]:
                template.append(self.createCordisOrganizations(entry))
        of = open(self.filename + '_output.ttl', 'w', encoding="utf-8")
        for line in template:
            of.write(line)
        of.close

    def createCordisProjects(self, entry):
        output = ('cordis:' + entry[0] + ' a dbc:ResearchProject;\n\t' +
                  'dbc:projectReferenceID\t' + entry[1] + ';\n\t' +
                  'doap:name\t' + entry[2] + ';\n\t' +
                  'dc:title\t' + entry[7] + ';\n\t')
        if len(entry[10]) > 1:
            output = output + 'doap:homepage\t' + entry[10] + ';\n\t'
        if len(entry[8]) > 1:
            output = output + ( 'dbc:projectStartDate\t' + entry[8].split('/')[2] + '-' + entry[8].split('/')[0] + '-' + entry[8].split('/')[1] + '^^xsd:date;\n\t' +
                                'dbc:projectEndDate\t' + entry[9].split('/')[2] + '-' + entry[9].split('/')[0] + '-' + entry[9].split('/')[1] + '^^xsd:date;\n\t')
            #'dc:PeriodOfTime\t' + str((date(int(entry[9].split('/')[2]), int(entry[9].split('/')[0]), int(entry[9].split('/')[1])) - date(int(entry[8].split('/')[2]), int(entry[8].split('/')[0]), int(entry[8].split('/')[1]))).days) + ';\n\t'
        if len(entry[3]) > 1:
            output = output + 'cordis:status\t' + self.transcribeStatus(entry[3]) + ';\n\t'
        output = output + ('cordis:programme\t' + entry[4] + ';\n\t' +
                           'cordis:frameworkProgramme\t' + entry[6] + ';\n\t' +
                           'cordis:projectTopics\t' + entry[5] + ';\n\t')
        if len(entry[14]) > 1:
            output = output + 'cordis:projectFundingScheme' + entry[14] + ';\n\t'
        output = output + ('dbc:projectBudgetFunding\t' + entry[13].replace(',','.') + '^^<http://dbpedia.org/datatype/euro>;\n\t' +
                           'dbc:projectBudgetTotal\t' + entry[12].replace(',','.') +'^^<http://dbpedia.org/datatype/euro>;\n\t' +
                           'dbc:projectCoordinator\t' + entry[16] + ';\n\t' +
                           'cordis:projectCoordinatorCountry\t' + 'dbr:' + self.alpha2Name(entry[17]) + ';\n\t')
        if len(entry[18]) > 1:
            for participant in entry[18].split(';'):
                output = output + '<http://dbpedia.org/ontology/projectParticipant>\t' + participant + ';\n\t'
        if len(entry[19]) > 1:
            for country in entry[19].split(';'):
                output = output + 'cordis:projectParticipantCountry\t' + 'dbr:' + self.alpha2Name(country) + ';\n\t'
        if len(entry[20]) > 1:
            for subject in entry[20].split(';'):
                output = output + 'cordis:projectSubject\t' + subject + ';\n\t'
        output = output + 'dbc:projectObjective\t' + entry[11] + ';\n\t.\n\n'
        return output

    def createCordisOrganizations(self, entry):
        output = ('cordis:' + entry[6] + entry[0] + ' a dbc:ResearchProject, doap:project, rdf:type;\n\t' +
                  'dbc:projectReferenceID\t' + self.setLiterals(entry[1]) + ';\n\t' +
                  'doap:name\t' + self.setLiterals(entry[2]) + ';\n\t'
                  # 'cordis:role\t' + entry[3] + ';\n\t'
                  'foaf:organization\t [cordis:organizationName\t' + self.setLiterals(entry[5]) + ';\n\t\t' +
                  'cordis:organizationShortName\t' + self.setLiterals(entry[6]) + ';\n\t\t')
        if len(entry[10]) > 1:
            output = output + 'cordis:organizationCountry\tdbr:' + self.alpha2Name(entry[10]) + ';\n\t\t'
        if len(entry[7]) > 1:
            output = output + 'cordis:activityType\t' + entry[7] + ';\n\t\t'
        if len(entry[8]) > 1:
            output = output + 'cordis:endOfParticipation\t' + entry[8] + ';\n\t\t'
        if len(entry[9]) > 1:
            output = output + 'dbc:projectBudgetFunding\t' + entry[9].split('.')[0] + '^^<http://dbpedia.org/datatype/euro>;\n\t\t'
        if len(entry[12]) > 1:
            output = output + 'dbc:locationCity\t' + '<http://dbpedia.org/page/' + self.capitalizeAll(entry[12]) + '>;\n\t'
        if len(entry[11]) > 1:
            output = output + 'dbo:address\t' + entry[11] + ';\n\t'
        if len(entry[13]) > 1:
            output = output + '<http://dbpedia.org/ontology/postalCode>\t' + entry[13] + ';\n\t'
        if len(entry[14]) > 1:
            output = output + 'cordis:organizationHomepage\t' + (entry[14][:4] != 'http')*'http://' + entry[14] + ';\n\t'
            # if len(entry[15]) > 1:
            #     output = output + 'cordis:contactType\t' + entry[15] +';\n\t'
        if len(entry[16]) > 1:
            output = output + 'foaf:title\t' + entry[16] + ';\n\t'
        if len(entry[17]) > 1:
            output = output + 'foaf:firstName\t' + entry[17] + ';\n\t'
        if len(entry[18]) > 1:
            output = output + 'foaf:lastName\t' + entry[18] + ';\n\t'
        if len(entry[20]) > 1:
            output = output + 'foaf:phone\t' + entry[20] + ';\n\t'
        if len(entry[21]) > 1:
            output = output + 'cordis:faxNumber\t' + entry[21] + ';\n\t'
        if len(entry[22]) > 1:
            output = output + 'foaf:mbox\t' + entry[22] + ';\n\t'
        output = output + '.\n\n'
        return output

    def parseCordisProject(self, entry, hostBene):
        Project = namedtuple('Project', 'identifier, referenceID, name, title, homepage, startDate, endDate, status, programme, frameworkProgramme, topics, fundingScheme, budgetTotal, budgetFunding, coordinator, participants, subjects, objective')
        project = []
        project.append(entry[0])
        project.append(entry[1])
        project.append(entry[2])
        project.append(entry[7])
        project.append(entry[10])
        project.append(entry[8])
        project.append(entry[9])
        if len(entry[3]) > 1:
            project.append(self.transcribeStatus(entry[3]))
        else:
            project.append('')
        project.append(entry[4])
        project.append(entry[6])
        project.append(entry[5])
        project.append(entry[14])
        project.append(entry[12])
        project.append(entry[13])
        project.append(entry[16])
        tmp = []
        for participant in entry[18].split(';'):
            tmp.append(participant)
        project.append(tmp)
        tmp2 = []
        for subject in entry[20].split(';'):
            tmp2.append(subject)
        project.append(tmp2)
        project.append(entry[11])
        return self.createProjectOutput(Project(*project), hostBene)

    def parseCordisOrganization(self, entry):
        Organization = namedtuple('Organization', 'identifier, referenceID, projectName, role, name, shortName, country, activityType, endOfParticipation, city, postalCode, street, homepage, contact')
        org = []
        org.append(entry[0])
        org.append(entry[1])
        org.append(entry[2])
        org.append(entry[3])
        org.append(entry[5])
        org.append(entry[6])
        if len(entry[10]) > 1:
            org.append(self.alpha2Name(entry[10]))
        else:
            org.append('')
        org.append(entry[7])
        org.append(entry[8])
        org.append('http://dbpedia.org/page/' + self.capitalizeAll(entry[12]))
        org.append(entry[13])
        org.append( entry[11])
        org.append((entry[14][:4] != 'http')*'http://' + entry[14])
        org.append(parse.quote_plus(entry[17] + entry[18] + entry[6]))
        output = Organization(*org)
        return [self.createOrganizationOutput(output), output.name, [output.role, output.identifier, output.name]]

    def parseCordisPerson(self, entry):
        Person = namedtuple('Person', 'type, title, firstName, lastName, phone, fax, mail, shortOrgName')
        person = []
        person.append(entry[15])
        person.append(entry[16])
        person.append(entry[17])
        person.append(entry[18])
        person.append(entry[20])
        person.append(entry[21])
        person.append(entry[22])
        person.append(entry[6])
        output = Person(*person)
        return [self.createPersonOutput(output)]

    def createCordisObjects(self, projectsData, organizationData):
        template = self.readTemplate('cordis_full_template.ttl')
        #projects = []
        #organizations = []
        #persons = []
        usedOrgs = []
        hostBene = []
        #usedPers = []
        #output = ''
        print('start')
        of = open('full_cordis.ttl', 'w', encoding="utf-8")
        for line in template:
            of.write(line)
        for i, organization in enumerate(organizationData[1:]):
            org = self.parseCordisOrganization(organization)
            per = self.parseCordisPerson(organization)
            if (not org[1] in usedOrgs):
                for line in org[0]:
                    of.write(line)
                usedOrgs.append(org[1])
                for line in per[0]:
                    of.write(line)
                if org[2][0] == 'hostInstitution' or org[2][0] == 'beneficiary':
                    hostBene.append(org[2])
            print(i)
        for i, project in enumerate(projectsData[1:]):
            for line in self.parseCordisProject(project, hostBene):
                of.write(line)
            print(i)
        of.close

    def parseCordisProjectRDF(self, entry, graph, hostBene):
        Project = namedtuple('Project', 'identifier, referenceID, name, title, homepage, startDate, endDate, status, programme, frameworkProgramme, topics, fundingScheme, budgetTotal, budgetFunding, coordinator, participants, subjects, objective')
        project = []
        project.append(entry[0])
        project.append(entry[1])
        project.append(entry[2])
        project.append(entry[7])
        project.append(entry[10])
        project.append(entry[8])
        project.append(entry[9])
        if len(entry[3]) > 1:
            project.append(self.transcribeStatus(entry[3]))
        else:
            project.append('')
        project.append(entry[4])
        project.append(entry[6])
        project.append(entry[5])
        project.append(entry[14])
        project.append(entry[12])
        project.append(entry[13])
        project.append(entry[16])
        tmp = []
        for participant in entry[18].split(';'):
            tmp.append(participant)
        project.append(tmp)
        tmp2 = []
        for subject in entry[20].split(';'):
            tmp2.append(subject)
        project.append(tmp2)
        project.append(entry[11])
        """
        Create triples
        """
        pro = Project(*project)
        proRDF = CPRO[pro.identifier]
        graph.add((proRDF, RDF.type, DBO.ResearchProject))
        graph.add((proRDF, DBO.projectReferenceID, Literal(self.setLiterals(pro.referenceID))))
        graph.add((proRDF, DOAP.name, Literal(self.setLiterals(pro.name))))
        graph.add((proRDF, RDFS.label, Literal(self.setLiterals(pro.name))))
        graph.add((proRDF, DC.title, Literal(self.setLiterals(pro.title))))
        if len(pro.homepage) > 1:
            if ';' in pro.homepage:
                for homepage in pro.homepage.split(';'):
                    graph.add((proRDF, DOAP.homepage, URIRef(self.setLiterals(homepage).replace('"','').replace("'",''))))
            if ',' in pro.homepage:
                for homepage in pro.homepage.split(','):
                    graph.add((proRDF, DOAP.homepage, URIRef(self.setLiterals(homepage).replace('"','').replace("'",''))))
        if len(pro.startDate) > 1:
            sDate = datetime.date(int(pro.startDate.split('/')[2]), int(pro.startDate.split('/')[0]), int(pro.startDate.split('/')[1]))
            eDate = datetime.date(int(pro.endDate.split('/')[2]), int(pro.endDate.split('/')[0]), int(pro.endDate.split('/')[1]))
            graph.add((proRDF, DBO.projectStartDate, Literal(sDate)))
            graph.add((proRDF, DBO.projectEndDate, Literal(eDate)))
        if len(pro.status) > 1:
            graph.add((proRDF, CORDIS.status, Literal(self.setLiterals(pro.status))))
        graph.add((proRDF, CORDIS.programme, Literal(self.setLiterals(pro.programme))))
        graph.add((proRDF, CORDIS.frameworkProgramme, Literal(self.setLiterals(pro.frameworkProgramme))))
        graph.add((proRDF, CORDIS.projectTopics, Literal(self.setLiterals(pro.topics))))
        if len(pro.fundingScheme) > 1:
            graph.add((proRDF, CORDIS.projectFundingScheme, Literal(self.setLiterals(pro.fundingScheme))))
        graph.add((proRDF, DBO.projectBudgetFunding,Literal(self.setLiterals(pro.budgetFunding.replace(',','.')))))
        graph.add((proRDF, DBO.projectBudgetTotal, Literal(self.setLiterals(pro.budgetTotal.replace(',','.')))))
        graph.add((proRDF, DBO.projectCoordinator, CORG[parse.quote_plus(pro.coordinator)]))
        if len(pro.participants) > 1:
            for participant in pro.participants:
                graph.add((proRDF, DBO.projectParticipant, CORG[parse.quote_plus(participant)]))
        for org in hostBene:
            if pro.identifier == org[1]:
                if org[0] == 'hostInstitution':
                    graph.add((proRDF, CORDIS.hostInstitution, CORG[parse.quote_plus(org[2])]))
                elif org[0] == 'beneficiary':
                    graph.add((proRDF, CORDIS.beneficiary, CORG[parse.quote_plus(org[2])]))
        if len(pro.subjects) > 1:
            for subject in pro.subjects:
                graph.add((proRDF, CORDIS.projectSubject, Literal(self.setLiterals(subject))))
        graph.add((proRDF, DBO.projectObjective, Literal(self.setLiterals(pro.objective))))
        #return self.createProjectOutput(Project(*project), hostBene)

    def parseCordisOrganizationRDF(self, entry, graph):
        Organization = namedtuple('Organization', 'identifier, referenceID, projectName, role, name, shortName, country, activityType, endOfParticipation, city, postalCode, street, homepage, contact, id')
        org = []
        org.append(entry[0])
        org.append(entry[1])
        org.append(entry[2])
        org.append(entry[3])
        org.append(entry[5])
        org.append(entry[6])
        if len(entry[10]) > 1:
            org.append(self.alpha2Name(entry[10]))
        else:
            org.append('')
        org.append(entry[7])
        org.append(entry[8])
        org.append('http://dbpedia.org/page/' + parse.quote(self.capitalizeAll(self.setLiterals(entry[12]))))
        org.append(entry[13])
        org.append( entry[11])
        org.append((entry[14][:4] != 'http')*'http://' + entry[14])
        org.append(parse.quote_plus(entry[17] + entry[18] + entry[6]))
        org.append(entry[4])
        organization = Organization(*org)
        """
        Create triples
        """
        if len(organization.id) > 1:
            orgRDF = CORG[self.setLiterals(organization.id)]
        else:
            orgRDF = CORG[parse.quote_plus(organization.name)]
        graph.add((orgRDF, RDF.type, FOAF.Organization))
        graph.add((orgRDF, CORDIS.organizationName, Literal(self.setLiterals(organization.name))))
        graph.add((orgRDF, CORDIS.organizationShortName, Literal(self.setLiterals(organization.shortName))))
        if len(organization.country) > 1:
            graph.add((orgRDF, CORDIS.organizationCountry, DBR[self.setLiterals(organization.country)]))
        if len(organization.activityType) > 1:
            graph.add((orgRDF, CORDIS.activityType, Literal(self.setLiterals(organization.activityType))))
        if len(organization.endOfParticipation) > 1:
            graph.add((orgRDF, CORDIS.endOfParticipation, Literal(self.setLiterals(organization.endOfParticipation))))
        if len(organization.city) > 1:
            graph.add((orgRDF, DBO.locationCity, URIRef(organization.city)))
        if len(organization.street) > 1:
            graph.add((orgRDF, DBO.address, Literal(self.setLiterals(organization.street))))
        if len(organization.postalCode) > 1:
            graph.add((orgRDF, DBO.postalCode, Literal(self.setLiterals(organization.postalCode))))
        if len(organization.homepage) > 1:
            if ';' in organization.homepage:
                for homepage in organization.homepage.split(';'):
                        graph.add((orgRDF, FOAF.homepage, URIRef(self.setLiterals(homepage).replace('"', '').replace("'",''))))
            if ',' in organization.homepage:
                for homepage in organization.homepage.split(','):
                        graph.add((orgRDF, FOAF.homepage, URIRef(self.setLiterals(homepage).replace('"', '').replace("'",''))))
        if len(organization.contact) > 1:
            graph.add((orgRDF, FOAF.person, CPEO[organization.contact]))
        return organization

    def parseCordisPersonRDF(self, entry, graph):
        Person = namedtuple('Person', 'type, title, firstName, lastName, phone, fax, mail, shortOrgName')
        person = []
        person.append(entry[15])
        person.append(entry[16])
        person.append(entry[17])
        person.append(entry[18])
        person.append(entry[20])
        person.append(entry[21])
        person.append(entry[22])
        person.append(entry[6])
        per = Person(*person)
        """
        create Triples
        """
        perRDF = CPEO[parse.quote_plus(per.firstName + per.lastName + per.shortOrgName)]
        graph.add((perRDF, RDF.type, FOAF.Person))
        if len(per.title) > 1:
            graph.add((perRDF, FOAF.title, Literal(self.setLiterals(per.title))))
        if len(per.firstName) > 1:
            graph.add((perRDF, FOAF.firstName, Literal(self.setLiterals(per.firstName))))
        if len(per.lastName) > 1:
            graph.add((perRDF, FOAF.lastName, Literal(self.setLiterals(per.lastName))))
        if len(per.firstName) > 1 and len(per.lastName) > 1:
            graph.add((perRDF, FOAF.name, Literal(self.setLiterals(per.firstName) + ' ' + self.setLiterals(per.lastName))))
        if len(per.phone) > 1:
            graph.add((perRDF, FOAF.phone, Literal(self.setLiterals(per.phone))))
        if len(per.fax) > 1:
            graph.add((perRDF, CORDIS.faxNumber, Literal(self.setLiterals(per.fax))))
        if len(per.mail) > 1:
            graph.add((perRDF, FOAF.mbox, URIRef(per.mail)))
        #return [self.createPersonOutput(output)]

    def createCordisObjectsRDF(self, projectsData, organizationData):
        usedOrgs = []
        hostBene = []
        graph = Graph()
        print('start')
        for i, organization in enumerate(organizationData[1:]):
            if (not organization[5] in usedOrgs):
                org = self.parseCordisOrganizationRDF(organization, graph)
                usedOrgs.append(org.name)
                self.parseCordisPersonRDF(organization, graph)
                if org.role == 'hostInstitution' or org.role == 'beneficiary':
                    hostBene.append([org.role, org.identifier, org.name])
            print(i)
        for i, project in enumerate(projectsData[1:]):
            self.parseCordisProjectRDF(project, graph, hostBene)
            print(i)
        graph.serialize('cordis_full_RDF.nt', format='nt')

    def createProjectOutput(self, project, hostBene):
        output = ('cordis:projects/' + project.identifier + ' a dbo:ResearchProject;\n\t' +
                  'dpro:projectReferenceID\t"' + self.setLiterals(project.referenceID) + '";\n\t' +
                  'doap:name\t"' + self.setLiterals(project.name) + '";\n\t' +
                  'rdfs:label\t"' + self.setLiterals(project.name) + '";\n\t' +
                  'dc:title\t"' + self.setLiterals(project.title) + '";\n\t')
        if len(project.homepage) > 1:
            output = output + 'doap:homepage\t<' + project.homepage + '>;\n\t'
        if len(project.startDate) > 1:
            output = output + ( 'dbo:projectStartDate\t"' + project.startDate.split('/')[2] + '-' + project.startDate.split('/')[0] + '-' + project.startDate.split('/')[1] + '"^^xsd:date;\n\t' +
                                'dbo:projectEndDate\t"' + project.endDate.split('/')[2] + '-' + project.endDate.split('/')[0] + '-' + project.endDate.split('/')[1] + '"^^xsd:date;\n\t')
        if len(project.status) > 1:
            output = output + 'cordis:status\t"' + project.status + '";\n\t'
        output = output + ('cordis:programme\t"' + self.setLiterals(project.programme) + '";\n\t' +
                           'cordis:frameworkProgramme\t"' + self.setLiterals(project.frameworkProgramme) + '";\n\t' +
                           'cordis:projectTopics\t"' + self.setLiterals(project.topics) + '";\n\t')
        if len(project.fundingScheme) > 1:
            output = output + 'cordis:projectFundingScheme\t"' + project.fundingScheme + '";\n\t'
        output = output + ('dbo:projectBudgetFunding\t' + project.budgetFunding.replace(',','.') + '^^<http://dbpedia.org/datatype/euro>;\n\t' +
                           'dbo:projectBudgetTotal\t' + project.budgetTotal.replace(',','.') +'^^<http://dbpedia.org/datatype/euro>;\n\t' +
                           'dbo:projectCoordinator\tcordis:organizations/' + parse.quote_plus(project.coordinator) + ';\n\t')
        if len(project.participants) > 1:
            for participant in project.participants:
                output = output + 'dbo:projectParticipant\tcordis:organizations/' + parse.quote_plus(participant) + ';\n\t'
        for org in hostBene:
            if project.identifier == org[1]:
                if org[0] == 'hostInstitution':
                    output = output + 'cordis:hostInstitution\tcordis:organizations/' + parse.quote_plus(org[2]) + ';\n\t'
                elif org[0] == 'beneficiary':
                    output = output + 'cordis:beneficiary\tcordis:organizations/' + parse.quote_plus(org[2]) + ';\n\t'
        if len(project.subjects) > 1:
            for subject in project.subjects:
                output = output + 'cordis:projectSubject\t"' + subject + '";\n\t'
        output = output + 'dbo:projectObjective\t"' + self.setLiterals(project.objective) + '";\n\t.\n\n'
        return output

    def createOrganizationOutput(self, organization):
        output = ('cordis:organizations/' + parse.quote_plus(organization.name) + ' a foaf:Organization, dbo:Organisation;\n\t' +
                  'cordis:organizationName\t"' + self.setLiterals(organization.name) + '";\n\t' +
                  'cordis:organizationShortName\t"' + self.setLiterals(organization.shortName) + '";\n\t')
        if len(organization.country) > 1:
            output = output + 'cordis:organizationCountry\tdbr:"' + organization.country + '";\n\t'
        if len(organization.activityType) > 1:
            output = output + 'cordis:activityType\t"' + self.setLiterals(organization.activityType) + '";\n\t'
        if len(organization.endOfParticipation) > 1:
            output = output + 'cordis:endOfParticipation\t"' + self.setLiterals(organization.endOfParticipation) + '";\n\t'
        if len(organization.city) > 1:
            output = output + 'dbo:locationCity\t<' + organization.city + '>;\n\t'
        if len(organization.street) > 1:
            output = output + 'dbo:address\t"' + self.setLiterals(organization.street) + '";\n\t'
        if len(organization.postalCode) > 1:
            output = output + 'dbo:postalCode\t"' + self.setLiterals(organization.postalCode) + '";\n\t'
        if len(organization.homepage) > 1:
            output = output + 'foaf:homepage\t<' + self.setLiterals(organization.homepage) + '>;\n\t'
        if len(organization.contact) > 1:
            output = output + 'foaf:person\tcordis:people/' + organization.contact
        output = output + '.\n\n'
        return output

    def createPersonOutput(self, person):
        output = 'cordis:people/' + parse.quote_plus(person.firstName + person.lastName + person.shortOrgName) + ' a foaf:Person;\n\t'
        if len(person.title) > 1:
            output = output + 'foaf:title\t"' + self.setLiterals(person.title) + '";\n\t'
        if len(person.firstName) > 1:
            output = output + 'foaf:firstName\t"' + self.setLiterals(person.firstName) + '";\n\t'
        if len(person.lastName) > 1:
            output = output + 'foaf:lastName\t"' + self.setLiterals(person.lastName) + '";\n\t'
        if len(person.phone) > 1:
            output = output + 'foaf:phone\t"' + self.setLiterals(person.phone) + '";\n\t'
        if len(person.fax) > 1:
            output = output + 'cordis:faxNumber\t"' + self.setLiterals(person.fax) + '";\n\t'
        if len(person.mail) > 1:
            output = output + 'foaf:mbox\t<' + person.mail + '>;\n\t'
        output = output + '.\n\n'
        return output

    def setLiterals(self, string):
        if string.startswith('"') and string.endswith('"'):
            string = string[1:-1]
        if string.startswith("'") and string.endswith("'"):
            string = string[1:-1]
        if string.startswith(' '):
            string = string[1:]
        if string.endswith(' '):
            string = string[:-1]
        return string

    def capitalizeAll(self, string):
        output = ''
        for word in string.split(' '):
            output = output + word.capitalize()
        return output

    """
    legacy
    """
    def setYesNoBool(self, yn):
        if yn == 'yes':
            return True
        else:
            return False

    def transcribeStatus(self, status):
        if status == 'ONG':
            return 'ongoing'
        elif status == 'CAN':
            return 'cancelled'
        else:
            return 'undefined'

    def transferQuartal(self, year, quartal):
        return str(int(year) + 1*(quartal == '4')) + '-' + '0'*(quartal != '3') + str((int(quartal)*3 + 1)%12) + '-01'

    def alpha2Name(self, alpha2):
        if alpha2 == 'UK':
            alpha2 = 'GB'
        if alpha2 == 'EL':
            alpha2 = 'GR'
        if alpha2 == 'FY':
            alpha2 = 'MK'
        if alpha2 == 'KO':
            alpha2 = 'KR'
        if alpha2 == 'XK':
            return 'Kosovo'
        if alpha2 == 'AN':
            return 'Netherlands_Antilles'
        return countries.get(alpha2).name.replace(' ','_')

    """
    Testmethod
    """
    def printData(self, data):
        output = "|"
        for line in data:
            for value in line:
                output = output + value + '\t|'
            output = output + '\n|'
        print(output)


def main():

    file = input('Name of .csv file:')
    cr = Csv2Rdf(file)
    if 'cordis' in file:
        #cr.createOutput(cr.readMultilineInput('ᛥ'))
        if 'projects' in file:
            projectsData = cr.readMultilineInput('ᛥ')
            cr.filename = 'cordis_organizations'
            organizationsData = cr.readMultilineInput('ᛥ')
        elif 'organizations' in file:
            organizationsData = cr.readMultilineInput('ᛥ')
            cr.filename = 'cordis_projects'
            projectsData = cr.readMultilineInput('ᛥ')
        cr.createCordisObjectsRDF(projectsData, organizationsData)
    else:
        cr.createOutput(cr.readTextInput(';'))
    """
    g = Graph()
    bob = URIRef("http://example.org/people/Bob")
    linda = URIRef("http://example.org/people/Linda")
    DBO = Namespace("http://dbpedia.org/ontology/")
    CORDIS = Namespace("http://www.freme-project.eu/datasets/cordis/")
    test = "FUG"
    CORG = Namespace(CORDIS.organizations + "/")
    print(CORDIS[test])
    print(CORG.orgname)
    g.add( (CORG.Orgname, RDF.type, FOAF.Organization) )
    g.add( (CORG.Orgname, RDF.type, DBO.Organisation) )
    g.add( (bob, FOAF.name, Literal('Bob')) )
    g.add( (bob, FOAF.knows, linda) )
    g.add( (linda, RDF.type, FOAF.Person) )
    g.add( (linda, FOAF.name, Literal('Linda') ) )
    print (g.serialize(format='turtle'))
    """
if __name__ == '__main__':
    main()