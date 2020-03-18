import os
from input.ACE_to_DRS_and_Rules import readACEFile
from ontology.ontology import Ontology

ACE = "input/ACE_in2.txt"
DRS = "input/DRS.txt"

ontology = Ontology(os.path.dirname(os.path.abspath(__file__)))

facts,rules,reasonerFacts = ontology.addInputsToOntology(readACEFile(ACE,DRS),open(ACE,"r"),open(DRS,"r"))

'''
QUERIES

ontology.getACE() - returns the string read from the ACE file
ontology.getDRS() - returns the string read from the DRS file

ontology.getInitialFacts() - returns a set() with all the instruction facts as strings
ontology.getInitialRules() - returns a set() with all the instruction rules as strings
ontology.getInitialReasonerFacts() - returns a set() with all the reasoner facts learned from the facts and rules as strings
'''

# start think
