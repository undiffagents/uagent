import subprocess,time

def getPrefix():
	return 'PREFIX :      <http://www.uganet.com/ontology#>\nPREFIX opla:  <http://ontologydesignpatterns.org/opla#>\nPREFIX owl:   <http://www.w3.org/2002/07/owl#>\nPREFIX rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\nPREFIX xsd:   <http://www.w3.org/2001/XMLSchema#>\nPREFIX rdfs:  <http://www.w3.org/2000/01/rdf-schema#>\n'

def startServer():
	print("Starting Fuseki server\n")
	subprocess.call(['gnome-terminal','--','java', '-jar', './ontology/fuseki-server.jar', '--update'])
	time.sleep(2)

def addACEinput(ACE):
	string = getPrefix()+'INSERT DATA\n{\n:initialInstruction rdf:type :Instruction .\n:initialInstruction :asACEString "' + " ".join(ACE.read().splitlines()) + '" .\n}'
	subprocess.call(['./ontology/s-update','--service=http://localhost:3030/uagent/update',string])
	ACE.close()

def addDRSinput(DRS):
	string = getPrefix()+'INSERT DATA\n{\n:initialInstruction rdf:type :Instruction .\n:initialInstruction :asDRSString "' + ";".join(DRS.read().splitlines()) + '" .\n}'
	subprocess.call(['./ontology/s-update','--service=http://localhost:3030/uagent/update',string])
	DRS.close()
