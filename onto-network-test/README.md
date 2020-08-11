
To run ontoTest.py, make sure that the Jena Fuseki server is already up and running; I also usually run the agent once to make sure it's fully populated with the schema (not sure if that's necessary).

Then, in another wsl window, run ontoInterpreterTest.py, then ontoTest.py - each of these has an important function
**ontoInterpreterTest.py** - pushes RDF based on the (modified) interpreter output in interpreterTest.txt to the server in order to "instantiate" some Items/ItemRoles, etc.
**ontoTest.py**  - queries the server to get all triples from it, ignores any of the triples that don't have "Instance" in the name (the current test marker to see if something is instantiated), and creates a networkx graph which then gets exported to a GraphML file so that it can be imported into KOIOS or viewed through Cytoscape.

Necessary dependencies:
**SparqlWrapper** - pip3 install SPARQLWrapper
**networkx** - pip3 install networkx

If you want to run the exported instantiation graph in KOIOS, then just copy the .graphml file and put it in the same directory as KOIOS' DRSProcessing.py file; at that point, running KOIOS should pull it in and use it.  If that doesn't happen for whatever reason, check the ControlPanel.py file - specifically CONTROL_USE_IMPORTED_GRAPH should be true, and CONST_IMPORT_GRAPH_FILE_NAME should be the name of the graphML file (without any file extensions).

For any questions or clarifications, contact Daniel Schmidt.

Explanation of the system:
This takes in a lightly modified version of Aaron's interpreter output, processes it, and converts it to a set of RDF triples in order to instantiate the data into the ontology.  The modifications on the interpreter mainly consist of using controlled tags, as well as introducing the creation of items before their use in an isPartOf, action, or other such tag. 

The system iterates through each line, creating RDF triples as is appropriate.  e.g., item(screen) = :InstanceItem0 rdf:type :Item . :InstanceItemRole0 rdf:type :ItemRole . :InstanceItemRole0 :ofType "screen" . :InstanceItemRole0 :assumedBy :InstanceItem0 .

Each action closes a situation, creates a new one (still need to figure out exactly what gets carried over from a previous situation into a new one), and links them with a transition triggered by the action.

Each new Situation gets a copy of all of the items in the prior Situation, as well as any new items which may have been developed.  There's a distinction made between situation-level elements (screen, letter) and experiment-level elements (task, possibly agent?)

This whole project is done with full awareness that I'm no expert on ontologies and may be going about instantiating the ontology incorrectly - rather, it serves a proof-of-concept for a way to get things end-to-end, as well as experimenting with Situations.

Another key point which needs figured out is how to deal with consequences of actions - specifically, when those consequences are another action or some kind of modification of an item, rather than simply creation of a new item (which is what has been used for testing).


> Written with [StackEdit](https://stackedit.io/).