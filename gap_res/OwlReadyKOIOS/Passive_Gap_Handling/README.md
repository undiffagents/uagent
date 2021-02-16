Initial Knowledge Graph validation system

Currently, a hardcoded list of expected neighbor nodes is used as a proof of concept test.  This program currently pulls down a copy of the ontology instantiation (using the same mechanism as ontoTest.py) and iterates through the graph in order to find neighboring nodes and check if all of the expected neighbors are present.  If not, the user is informed.

Next steps: Don't use a hardcoded version of the expected relationships and base it off of an automated check somehow.  Also resolution in some instances?

To run, ensure that the Jena Fuseki server is running, as well as filled with an instantiated version of the knowledge graph.

Basic workflow for this (on my machine, and possibly including unnecessary steps, I haven't fully vetted it):
    In one WSL window, run 'python3 interpreter/interpreter.py' in uagent-new
    In another window, run 'python3 gap_res/OwlReadyKOIOS/dlGraphInitializer.py' to instantiate data into the knowledge graph
    Finally, for KG validation, run 'python3 gap_res/OwlReadyKOIOS/Passive_Gap_Handling/KG_Structure_Validation.py' in uagent-new.

NOTE: Some variables/filepaths in the gap_res portions are absolutely machine-specific to my drive structure, etc. so there may need to be some minor edits
