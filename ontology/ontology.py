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
		subprocess.call(['ontology/s-update','--service=http://localhost:3030/uagent/update',"LOAD <file://"+here+"/ontology/uagent.owl>"])
		return server
	
	def queryOntologyForObject(self,query):
		return set([ x['object']['value'] for x in json.loads(subprocess.run(['ontology/s-query','--service','http://localhost:3030/uagent/query',self.getPrefix()+"SELECT ?object WHERE"+query], capture_output=True).stdout.decode('utf-8'))['results']['bindings'] ])
	
	def addToOntology(self,inputs):
		subprocess.call(['ontology/s-update','--service=http://localhost:3030/uagent/update',self.getPrefix()+"INSERT DATA "+inputs])
	
	def getPrefix(self):
		return 'PREFIX : <http://www.uagent.com/ontology#>\nPREFIX opla:  <http://ontologydesignpatterns.org/opla#>\nPREFIX owl: <http://www.w3.org/2002/07/owl#>\nPREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\nPREFIX xsd: <http://www.w3.org/2001/XMLSchema#>\nPREFIX rdfs:  <http://www.w3.org/2000/01/rdf-schema#>\n'
	
	def addACEFileInput(self,ACEFile):
		self.addToOntology('{ :initialInstruction rdf:type :Instruction . :initialInstruction :asACEString "' + "\\n".join(ACEFile.read().splitlines()) + '" .}')	
		ACEFile.close()
	
	def addDRSFileInput(self,DRSFile):
		self.addToOntology("{ :initialInstruction rdf:type :Instruction . :initialInstruction :asDRSString '" + "\\n".join(DRSFile.read().splitlines()) + "' . }")
		DRSFile.close()
	
	def addInitialRule(self,rule):
		self.addToOntology("{ :initialInstruction rdf:type :Instruction . :initialInstruction :asRuleString '" + rule + "' . }")
		
	def addInitialGroundRule(self,rule):
		self.addToOntology("{ :initialInstruction rdf:type :Instruction . :initialInstruction :asGroundRuleString '" + rule + "' . }")	
	
	def addInitialFact(self,fact):
		self.addToOntology("{ :initialInstruction rdf:type :Instruction . :initialInstruction :asFactString '" + fact + "' . }")
	
	def addInitialReasonerFact(self,newFact):
		self.addToOntology("{ :initialInstruction rdf:type :Instruction . :initialInstruction :asReasonerFactString '" + newFact + "' . }")
		
	def addInputsToOntology(self,aceFileOutput,aceFileIn,drsFileIn):
		facts,rules,groundRules,newFacts = aceFileOutput
		for fact in facts:
			self.addInitialFact(fact)
		for rule in rules:
			self.addInitialRule(rule)
		for rule in groundRules:
			self.addInitialGroundRule(rule)
		for newFact in newFacts:
			self.addInitialReasonerFact(newFact)
		self.addACEFileInput(aceFileIn)
		self.addDRSFileInput(drsFileIn)
		return facts,rules,groundRules,newFacts
	
	def getInitialRules(self):
		return self.queryOntologyForObject("{ :initialInstruction :asRuleString ?object . }")
	
	def getInitialGroundRules(self):
		return self.queryOntologyForObject("{ :initialInstruction :asGroundRuleString ?object . }")	
		
	def getInitialFacts(self):
		return self.queryOntologyForObject("{ :initialInstruction :asFactString ?object . }")
	
	def getInitialReasonerFacts(self):
		return self.queryOntologyForObject("{ :initialInstruction :asReasonerFactString ?object . }")
  
	def getDRS(self):
		return "".join(self.queryOntologyForObject("{ :initialInstruction :asDRSString ?object . }"))
	
	def getACE(self):
		return "".join(self.queryOntologyForObject("{ :initialInstruction :asACEString ?object . }"))	

