Initial Knowledge Graph validation system

Currently, a hardcoded list of expected neighbor nodes is used as a proof of concept test.  This program currently pulls down a copy of the ontology instantiation (using the same mechanism as ontoTest.py) and iterates through the graph in order to find neighboring nodes and check if all of the expected neighbors are present.  If not, the user is informed.

Next steps: Don't use a hardcoded version of the expected relationships and base it off of an automated check somehow.  Also resolution in some instances?