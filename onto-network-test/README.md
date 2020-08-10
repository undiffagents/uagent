
To run ontoTest.py, make sure that the Jena Fuseki server is already up and running; I also usually run the agent once to make sure it's fully populated with the schema (not sure if that's necessary).

Then, in another wsl window, run ontoInterpreterTest.py, then ontoTest.py - each of these has an important function
**ontoInterpreterTest.py** - pushes RDF based on the (modified) interpreter output in interpreterTest.txt to the server in order to "instantiate" some Items/ItemRoles, etc.
**ontoTest.py**  - queries the server to get all triples from it, ignores any of the triples that don't have "Instance" in the name (the current test marker to see if something is instantiated), and creates a networkx graph which then gets exported to a GraphML file so that it can be imported into KOIOS or viewed through Cytoscape.

Necessary dependencies:
**SparqlWrapper** - pip3 install SPARQLWrapper
**networkx** - pip3 install networkx

If you want to run the exported instantiation graph in KOIOS, then just copy the .graphml file and put it in the same directory as KOIOS' DRSProcessing.py file; at that point, running KOIOS should pull it in and use it.  If that doesn't happen for whatever reason, check the ControlPanel.py file - specifically CONTROL_USE_IMPORTED_GRAPH should be true, and CONST_IMPORT_GRAPH_FILE_NAME should be the name of the graphML file (without any file extensions).

For any questions or clarifications, contact Daniel Schmidt.

> Written with [StackEdit](https://stackedit.io/).