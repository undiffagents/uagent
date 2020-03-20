import json
import os
import socket
import subprocess


class Ontology:
	
	prefix = 'PREFIX : <http://www.uagent.com/ontology#>\nPREFIX opla: <http://ontologydesignpatterns.org/opla#>\nPREFIX owl: <http://www.w3.org/2002/07/owl#>\nPREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\nPREFIX xsd: <http://www.w3.org/2001/XMLSchema#>\nPREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n'
	initialInstruction = ':initialInstruction'
	initialInstructionType = '{} rdf:type :Instruction .'.format(initialInstruction)

	def __init__(self, filename='uagent.owl'):
		self._load(filename)

	def _load(self, filename):
		print('Waiting for ontology server...')
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
			while s.connect_ex(('localhost', 3030)) > 0:
				pass
		print('Loading ontology...')
		path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
		subprocess.call(['lib/fuseki/s-update','--service=http://localhost:3030/uagent/update',"LOAD <file://"+path+">"])
		return self
	
	def queryOntologyForObject(self, query):
		results = subprocess.run(['lib/fuseki/s-query', '--service', 'http://localhost:3030/uagent/query',
								  '{} SELECT ?object WHERE {{ {} }}'.format(self.prefix, query)],
                                  stdout=subprocess.PIPE).stdout.decode('utf-8')
		bindings = json.loads(str(results))['results']['bindings']
		return set([x['object']['value'] for x in bindings])
	
	def addToOntology(self,inputs):
		subprocess.call(['lib/fuseki/s-update','--service=http://localhost:3030/uagent/update','{} INSERT DATA  {{ {} }}'.format(self.prefix,inputs)])
	
	def addACEFileInput(self,ACE):
		self.addToOntology('{} {} :asACEString "{}" .'.format(self.initialInstructionType,self.initialInstruction,"\\n".join(open(ACE,"r").read().splitlines())))
	
	def addDRSFileInput(self,DRS):
		self.addToOntology('{} {} :asDRSString "{}" .'.format(self.initialInstructionType,self.initialInstruction,"\\n".join(open(DRS,"r").read().splitlines())))
	
	def addInitialRule(self,rule):
		self.addToOntology('{} {} :asRuleString "{}" .'.format(self.initialInstructionType,self.initialInstruction,rule))
		
	def addInitialGroundRule(self,rule):
		self.addToOntology('{} {} :asGroundRuleString "{}" .'.format(self.initialInstructionType,self.initialInstruction,rule))	
	
	def addInitialFact(self,fact):
		self.addToOntology('{} {} :asFactString "{}" .'.format(self.initialInstructionType,self.initialInstruction,fact))
	
	def addInitialReasonerFact(self,newFact):
		self.addToOntology('{} {} :asReasonerFactString "{}" .'.format(self.initialInstructionType,self.initialInstruction,newFact))
		
	def addInputsToOntology(self,aceFileOutput,aceFileIn,drsFileIn):
		print("Adding Inputs To Ontology\n")
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
		return self.queryOntologyForObject(":initialInstruction :asRuleString ?object .")
	
	def getInitialGroundRules(self):
		return self.queryOntologyForObject(":initialInstruction :asGroundRuleString ?object .")	
		
	def getInitialFacts(self):
		return self.queryOntologyForObject(":initialInstruction :asFactString ?object .")
	
	def getInitialReasonerFacts(self):
		return self.queryOntologyForObject(":initialInstruction :asReasonerFactString ?object .")
  
	def getDRS(self):
		return "".join(self.queryOntologyForObject(":initialInstruction :asDRSString ?object ."))
	
	def getACE(self):
		return "".join(self.queryOntologyForObject(":initialInstruction :asACEString ?object ."))	
