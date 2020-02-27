import os,sys

here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,here+"/ontology")
sys.path.insert(0,here+"/input")

from ACE_to_DRS_and_Rules import *
from ontology import *

ACE = "input/ACE_in2.txt"
DRS = "input/DRS.txt"
facts,rules,reasonerFacts = readACEFile(ACE,DRS)

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
'''

# start think
