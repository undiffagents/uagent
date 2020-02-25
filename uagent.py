import os,sys

here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,here+"/input")
sys.path.insert(0,here+"/ares")
sys.path.insert(0,here+"/ontology")
sys.path.insert(0,here+"/think")
sys.path.insert(0,here+"/input")
sys.path.insert(0,here+"/tasks")
sys.path.insert(0,here+"/ua")

from ACE_to_DRS_and_Rules import *
from ontology import *

ACE = "./input/ACE_in2.txt"
DRS = "./input/DRS.txt"
facts,rules,reasonerFacts = readACEFile(ACE,DRS)

startServer()

addACEinput(open(ACE,"r"))
addDRSinput(open(DRS,"r"))
addRulesinput(facts,rules,reasonerFacts)

# start think
