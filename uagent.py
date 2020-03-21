from ontology import Ontology
from interpreter import Interpreter

ontology = Ontology()
interpreter = Interpreter(ontology)

with open('input/ACE.txt', 'r') as f:
    ace = f.read()
    interpreter.interpret_ace(ace)

for rule in ontology.get_ground_rules():
    print(rule)

# start think
