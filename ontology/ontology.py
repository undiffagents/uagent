import json
import os
import re
import socket
import subprocess


class Ontology:

    PREFIX = 'PREFIX : <http://www.uagent.com/ontology#>\nPREFIX opla: <http://ontologydesignpatterns.org/opla#>\nPREFIX owl: <http://www.w3.org/2002/07/owl#>\nPREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\nPREFIX xsd: <http://www.w3.org/2001/XMLSchema#>\nPREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n'
    initialInstruction = ':initialInstruction'
    initialInstructionType = '{} rdf:type :Instruction .'.format(initialInstruction)

    def __init__(self):
        self.initialized = False

    def load(self, filename='uagent.owl'):
        print('Waiting for ontology server...')
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            while s.connect_ex(('localhost', 3030)) > 0:
                pass
        print('Loading ontology...')
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        subprocess.call(['lib/fuseki/s-update','--service=http://localhost:3030/uagent/update', "LOAD <file://{}>".format(path)])
        return self

    def add(self,data):
        subprocess.call(['lib/fuseki/s-update', '--service=http://localhost:3030/uagent/update','{} INSERT DATA  {{ {} }}'.format(self.PREFIX,data)])

    def add_string(self, subject,predicate,string):
        self.add('{} {} "{}" .'.format(subject,predicate,string))

    def add_file_object(self,path,subject,predicate):
        with open(path, 'r') as f:
            self.add_string(subject,predicate,'\\n'.join(f.read().splitlines()))

    def add_instruction_knowledge(self,ace_output):
        if not self.initialized:
        
            print("Adding knowledge to ontology...")
            
            facts,rules,groundRules,newFacts = ace_output

            self.add(self.initialInstructionType)

            for fact in facts:
                self.add_string(self.initialInstruction,':asFactString',fact)
            for rule in rules:
                self.add_string(self.initialInstruction,':asRuleString',rule)
            for rule in groundRules:
                self.add_string(self.initialInstruction,':asGroundRuleString',rule)
            for newFact in newFacts:
                self.add_string(self.initialInstruction,':asReasonerFactString',newFact)
            
            # self.add_string(self.initialInstruction,':asFactString',aceFile)
            # self.add_string(self.initialInstruction,':asFactString',drsFileIn)
            
            self.initialized = True
            
            return facts,rules,groundRules,newFacts

    def query(self,query):
        results = subprocess.run(['lib/fuseki/s-query','--service','http://localhost:3030/uagent/query',query],stdout=subprocess.PIPE).stdout.decode('utf-8')
        return json.loads(str(results))['results']['bindings']

    def query_for_object(self,subject,predicate):
        result = self.query('{} SELECT ?object WHERE {{ {} {} ?object . }}'.format(self.PREFIX,subject,predicate))        
        return set([x['object']['value'] for x in result])

    def get_instruction_facts(self):
        if self.initialized: return self.query_for_object(self.initialInstruction,':asFactString')

    def get_instruction_reasoner_facts(self):
        if self.initialized: return self.query_for_object(self.initialInstruction,':asReasonerFactString')

    def get_instruction_rules(self):
        if self.initialized: return self.query_for_object(self.initialInstruction,':asRuleString')

    def get_instruction_ground_rules(self):
        if self.initialized: return self.query_for_object(self.initialInstruction,':asGroundRuleString')

    def get_DRS(self):
        if self.initialized: return "".join(self.query_for_object(self.initialInstruction,":asDRSString"))

    def get_ACE(self):
        if self.initialized: return "".join(self.query_for_object(self.initialInstruction,":asACEString"))
