import os,sys

here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,os.path.join(here,"ontology"))
sys.path.insert(0,os.path.join(here,"input"))

#Revise to not use wildcard imports?
from ACE_to_DRS_and_Rules import * #readAceFile()
from ontology import * #everything else


ACE = "input/ACE_in2.txt"
DRS = "input/DRS.txt"
facts,rules,reasonerFacts = readACEFile(ACE,DRS)

#Instantiate Ontology server instance
ontologyThread = startServer(here)

addACEFileInput(open(ACE,"r"))
addDRSFileInput(open(DRS,"r"))
addRulesInput(facts,rules,reasonerFacts)

'''
AVAILABLE QUERIES
getInitialFacts() - returns a set() with all the instruction facts
getInitialRules() - returns a set() with all the instruction rules
getInitialReasonerFacts() - returnss a set() with all the reasoner facts learned from the facts and rules
# NOTE # These three are returned by the readACEFile() function and the data is already available

MANUAL QUERY EXAMPLE:
open localhost:3030 in a web browser.
Select Datatset, enter the following in the query box, hit play button:
# PREFIX :      <http://www.uagent.com/ontology#>
# PREFIX opla:  <http://ontologydesignpatterns.org/opla#>
# PREFIX owl:   <http://www.w3.org/2002/07/owl#>
# PREFIX rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
# PREFIX xsd:   <http://www.w3.org/2001/XMLSchema#>
# PREFIX rdfs:  <http://www.w3.org/2000/01/rdf-schema#>
# SELECT ?predicate ?object WHERE { :initialInstruction ?predicate ?object . }
'''

# start think
