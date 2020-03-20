import os
from input.ACE_to_DRS_and_Rules import readACEFile
from ontology.ontology import Ontology

ACE = "input/ACE.txt"
DRS = "input/DRS.txt"

ontology = Ontology(os.path.dirname(os.path.abspath(__file__)))

facts,rules,groundRules,reasonerFacts = ontology.addInputsToOntology(readACEFile(ACE,DRS),ACE,DRS)

for rule in ontology.getInitialRules():
    print(rule)

'''
QUERIES

ontology.getACE() - returns the string read from the ACE file
ontology.getDRS() - returns the string read from the DRS file

ontology.getInitialFacts() - returns a set() with all the instruction facts as strings
ontology.getInitialRules() - returns a set() with all the instruction rules as strings
ontology.getInitialGroundRules() - returns a set() with all the instruction SOLVED rules as strings
ontology.getInitialReasonerFacts() - returns a set() with all the reasoner facts learned from the facts and rules as strings

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
