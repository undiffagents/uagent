import subprocess,time,json,threading

class FusekiServer(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)

	def run(self):
		subprocess.call(['java', '-jar', 'ontology/fuseki-server.jar','--update'])
		
class Ontology:
	def __init__(self,here):
		self.ontology = self.startServer(here)
		
	def startServer(self,here):
		print("Starting Ontology server\n")
		server = FusekiServer()
		server.start()
		time.sleep(3)
		self.addToOntology("LOAD <file://"+here+"/ontology/uagent.owl>")
		return server
	
	def queryOntologyForObject(self,query):
		return set([ x['object']['value'] for x in json.loads(subprocess.run(['ontology/s-query','--service','http://localhost:3030/uagent/query',query], capture_output=True).stdout.decode('utf-8'))['results']['bindings'] ])
	
	def addToOntology(self,inputs):
		subprocess.call(['ontology/s-update','--service=http://localhost:3030/uagent/update',inputs])
	
	def getPrefix(self):
		return 'PREFIX : <http://www.uagent.com/ontology#>\nPREFIX opla:  <http://ontologydesignpatterns.org/opla#>\nPREFIX owl: <http://www.w3.org/2002/07/owl#>\nPREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\nPREFIX xsd: <http://www.w3.org/2001/XMLSchema#>\nPREFIX rdfs:  <http://www.w3.org/2000/01/rdf-schema#>\n'
	
	def addACEFileInput(self,ACEFile):
		self.addToOntology(self.getPrefix()+'INSERT DATA\n{\n:initialInstruction rdf:type :Instruction .\n:initialInstruction :asACEString "' + "\\n".join(ACEFile.read().splitlines()) + '" .\n}')	
		ACEFile.close()
	
	def addDRSFileInput(self,DRSFile):
		self.addToOntology(self.getPrefix()+"INSERT DATA\n{\n:initialInstruction rdf:type :Instruction .\n:initialInstruction :asDRSString '" + "\\n".join(DRSFile.read().splitlines()) + "' .\n}")
		DRSFile.close()
	
	def addInitialRule(self,rule):
		self.addToOntology(self.getPrefix()+"INSERT DATA\n{\n:initialInstruction rdf:type :Instruction .\n:initialInstruction :asRuleString '" + rule + "' .\n}")
	
	def addInitialFact(self,fact):
		self.addToOntology(self.getPrefix()+"INSERT DATA\n{\n:initialInstruction rdf:type :Instruction .\n:initialInstruction :asFactString '" + fact + "' .\n}")
	
	def addInitialReasonerFact(self,newFact):
		self.addToOntology(self.getPrefix()+"INSERT DATA\n{\n:initialInstruction rdf:type :Instruction .\n:initialInstruction :asReasonerFactString '" + newFact + "' .\n}")
		
	def addInputsToOntology(self,aceFileOutput,aceFileIn,drsFileIn):
		facts,rules,newFacts = aceFileOutput
		for fact in facts:
			self.addInitialFact(fact)
		for rule in rules:
			self.addInitialRule(rule)
		for newFact in newFacts:
			self.addInitialReasonerFact(newFact)
		self.addACEFileInput(aceFileIn)
		self.addDRSFileInput(drsFileIn)
		return facts,rules,newFacts
	
	def getInitialRules(self):
		return self.queryOntologyForObject(self.getPrefix()+"SELECT ?object WHERE { :initialInstruction :asRuleString ?object . }")
		
	def getInitialFacts(self):
		return self.queryOntologyForObject(self.getPrefix()+"SELECT ?object WHERE { :initialInstruction :asFactString ?object . }")
	
	def getInitialReasonerFacts(self):
		return self.queryOntologyForObject(self.getPrefix()+"SELECT ?object WHERE { :initialInstruction :asReasonerFactString ?object . }")
  
	def getDRS(self):
		return "".join(self.queryOntologyForObject(self.getPrefix()+"SELECT ?object WHERE { :initialInstruction :asDRSString ?object . }"))
	
	def getACE(self):
		return "".join(self.queryOntologyForObject(self.getPrefix()+"SELECT ?object WHERE { :initialInstruction :asACEString ?object . }"))	

