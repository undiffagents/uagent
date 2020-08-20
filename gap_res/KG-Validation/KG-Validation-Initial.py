import re
import networkx
from SPARQLWrapper import SPARQLWrapper, JSON
from owlready2 import *

from ontoConstants import *

# Initially hardcoding the structure of some links in the ontology just to test this system out on Items/Actions/etc.
# Some of these may not be quite 'necessary' - e.g. Affordances for items.
importantNodeSets = {ITEM_NODE: [ITEM_ROLE_NODE, AFFORDANCE_NODE, ITEM_DESCRIPTION_NODE],
                    ACTION_NODE: [ITEM_NODE, TRANSITION_DESCRIPTION_NODE],
                    ITEM_DESCRIPTION_NODE: [ITEM_LOCATION_NODE, ITEM_COLOR_NODE, ITEM_SHAPE_NODE, ITEM_TYPE_NODE]}


def checkInitializedGraph():
    testGraph = networkx.MultiDiGraph()
    testImport(testGraph)
    for nodeType in importantNodeSets:
        print("Expected nodes to be connected to " + nodeType + " nodes:")
        print(importantNodeSets.get(nodeType))
        print('\n')
    print('\n')
    # Iterate through all nodes.  If a key name is found, get the node "n"'s predecessors and successors.
    # Predecessor = directed edge from predecessor m to n, successor = directed edge from n to successor m.
    # Check that all of the nodes in the value array exist as pred/succ.
    for node in testGraph:
        # This is messy and not great but whatever for now, it's proof-of-concept
        for nodeSymbol in importantNodeSets.keys():
            # If found something from one of the keys
            nodeOfSetTypeFound = re.search(r'^' + nodeSymbol + r'\d+', node)
            if nodeOfSetTypeFound:
                # Get the list of successors and predecessors and check that all of the value array nodes are present
                preds = list(testGraph.predecessors(node))
                succs = list(testGraph.successors(node))
                neighborNodes = preds + succs
                # Default state is true - if one of the expected nodes is not found, then a flag is raised
                nodeIsConnected = True
                listOfMissingNodes = []
                for expectedNode in importantNodeSets.get(nodeSymbol):
                    # If the expected node is not found as a neighbord to the current node
                    foundConnectedNode = any(re.search(r'^' + expectedNode + r'\d+', nNode) for nNode in neighborNodes)
                    # Then mark that the current node is not fully connected and track which nodes are missing
                    if foundConnectedNode == False:
                        nodeIsConnected = False
                        listOfMissingNodes.append(expectedNode)
                # If the node is fully connected, it's good
                # If the node is not fully connected, then flag it to the user and inform them of what's missing
                if nodeIsConnected == True:
                    print(node + " fully connected.")
                else:
                    print("WARNING: " + node + " not fully connected.  Expected nodes not found: "
                          + str(listOfMissingNodes))


def addToGraph(testGraph, subjValue, predValue, objValue):
    # print("enter")
    subjFound = find_node(testGraph, 'value', subjValue)
    objFound = find_node(testGraph, 'value', objValue)
    if not subjFound:
        testGraph.add_node(subjValue, value=subjValue)
    if not objFound:
        testGraph.add_node(objValue, value=objValue)
    subjectNode = testGraph[subjValue]
    objectNode = testGraph[objValue]
    # print(testGraph.nodes)
    # print(subjectNode + " - edge to " + objectNode)
    testGraph.add_edge(subjValue, objValue, value=predValue)


# print("added" + subjectNode)

# https://stackoverflow.com/questions/49103913/check-whether-a-node-exists-in-networkx
def find_node(graph, attribute, value):
    return any([node for node in graph.nodes(data=True) if node[1][attribute] == value])


def testImport(testGraph):
    # testGraph = networkx.MultiDiGraph()
    # Set up sparql query
    sparql = SPARQLWrapper("http://localhost:3030/uagent")
    sparql.setQuery("""
		PREFIX :      <http://www.uagent.com/ontology#>
		PREFIX opla:  <http://ontologydesignpatterns.org/opla#>
		PREFIX owl:   <http://www.w3.org/2002/07/owl#>
		PREFIX rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
		PREFIX xsd:   <http://www.w3.org/2001/XMLSchema#>
		PREFIX rdfs:  <http://www.w3.org/2000/01/rdf-schema#>

		SELECT ?subj ?predicate ?object {
		  ?subj ?predicate ?object .
		   }
	""")
    sparql.setReturnFormat(JSON)
    # Get results of sparql query
    results = sparql.query().convert()

    # Iterate through results
    for result in results["results"]["bindings"]:
        # Look for "Instance" term
        instanceRelevant = False
        # Get subj/pred/obj
        subjValue = result["subj"]["value"]
        predValue = result["predicate"]["value"]
        objValue = result["object"]["value"]
        # If not an Instance, ignore
        if "Instance" in subjValue or "Instance" in predValue or "Instance" in objValue:
            instanceRelevant = True
        # Put literals in quotes
        if result["subj"]["type"] == 'literal':
            subjValue = '"' + subjValue + '"'
        if result["predicate"]["type"] == 'literal':
            predValue = '"' + predValue + '"'
        if result["object"]["type"] == 'literal':
            objValue = '"' + objValue + '"'

        # If an instance, print
        if instanceRelevant == True:
            # Trim off uri if there is an http://
            if "http://" in subjValue:
                # Only grab what's after the pound sign
                subjValue = subjValue.split('#')[1]
            # Strip off the word "Instance" from the beginning of the word
            subjValue = re.sub('^Instance', '', subjValue)
            # If there are quotes at the beginning or end of the string, remove them
            subjValue = subjValue.replace('"', '')

            if "http://" in predValue:
                # Only grab what's after the pound sign
                predValue = predValue.split('#')[1]
            # Strip off the word "Instance" from the beginning of the word
            predValue = re.sub('^Instance', '', predValue)
            # If there are quotes at the beginning or end of the string, remove them
            predValue = predValue.replace('"', '')

            if "http://" in objValue:
                # Only grab what's after the pound sign
                objValue = objValue.split('#')[1]
            # Strip off the word "Instance" from the beginning of the word
            objValue = re.sub('^Instance', '', objValue)
            # If there are quotes at the beginning or end of the string, remove them
            objValue = objValue.replace('"', '')

            # Testing removing rdf:type parts to make the graph less cluttered.
            # TODO: remove?
            # This apparently ignores stuff that's just created (Item6 type Item) and nothing else.  maybe ok?
            # if predValue != 'type':
            addToGraph(testGraph, subjValue, predValue, objValue)
            # print(subjValue + " - " + predValue + " - " + objValue)

    # testGraph.add_node(0, value='xyz')
    # testGraph.add_node(1, value='abc')
    # testGraph.add_edge(0, 1, value='edgy')
    #if testGraph is not None:
        # jsonFile = open("jsonFile.txt", "w")
        # jsonSerializable = networkx.readwrite.json_graph.node_link_data(testGraph.graph)
        # jsonOutput = json.dumps(jsonSerializable)
        # jsonFile.write(jsonOutput)
        # print(testGraph.nodes)
        # networkx.write_graphml(testGraph, "test.graphml")

checkInitializedGraph()