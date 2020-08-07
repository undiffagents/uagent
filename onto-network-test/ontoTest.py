import json
import os
import re
import socket
import subprocess
import time
import requests
import networkx
from SPARQLWrapper import SPARQLWrapper, JSON

def updateOnto():
	# Read my file of ontology test additions
	totalString = ''
	file1 = open('ontoTestAddition.txt', 'r')
	Lines = file1.readlines()
	# Get them ready to send up
	for line in Lines:
		line = line.strip()
		totalString += line + " ."
	totalString = totalString[:-1]
	print(totalString)
	PREFIX = 'PREFIX : <http://www.uagent.com/ontology#>\nPREFIX opla: <http://ontologydesignpatterns.org/opla#>\nPREFIX owl: <http://www.w3.org/2002/07/owl#>\nPREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\nPREFIX xsd: <http://www.w3.org/2001/XMLSchema#>\nPREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n'

	# Send em
	subprocess.call(['./s-update', '--service=http://localhost:3030/uagent/update',
					 '{} INSERT DATA  {{ {} }}'.format(PREFIX, totalString)])

def addToGraph(testGraph, subjValue, predValue, objValue):
	#print("enter")
	subjFound = find_node(testGraph, 'value', subjValue)
	objFound = find_node(testGraph, 'value', objValue)
	if not subjFound:
		testGraph.add_node(subjValue, value=subjValue)
	if not objFound:
		testGraph.add_node(objValue, value=objValue)
	subjectNode = testGraph[subjValue]
	objectNode = testGraph[objValue]
	#print(testGraph.nodes)
	#print(subjectNode + " - edge to " + objectNode)
	testGraph.add_edge(subjValue, objValue, value=predValue)
	#print("added" + subjectNode)

# https://stackoverflow.com/questions/49103913/check-whether-a-node-exists-in-networkx
def find_node(graph, attribute, value):
	return any([node for node in graph.nodes(data=True) if node[1][attribute] == value])

def testImport():
	testGraph = networkx.MultiDiGraph()
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
			if predValue != 'type':
				addToGraph(testGraph, subjValue, predValue, objValue)
				print(subjValue + " - " + predValue + " - " + objValue)

	#testGraph.add_node(0, value='xyz')
	#testGraph.add_node(1, value='abc')
	#testGraph.add_edge(0, 1, value='edgy')
	if testGraph is not None:
		# jsonFile = open("jsonFile.txt", "w")
		# jsonSerializable = networkx.readwrite.json_graph.node_link_data(testGraph.graph)
		# jsonOutput = json.dumps(jsonSerializable)
		# jsonFile.write(jsonOutput)
		print(testGraph.nodes)
		networkx.write_graphml(testGraph, "testNoType.graphml")

updateOnto()
testImport()