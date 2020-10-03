import json
import os
import re
import socket
import subprocess
import time


class Ontology:

    instructionGraph = ':instruction'
    koiosGraph = ':koios'
    thinkGraph = ':think'
    
    PREFIX = 'PREFIX : <http://www.uagent.com/ontology#>\nPREFIX opla: <http://ontologydesignpatterns.org/opla#>\nPREFIX owl: <http://www.w3.org/2002/07/owl#>\nPREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\nPREFIX xsd: <http://www.w3.org/2001/XMLSchema#>\nPREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n'

    def __init__(self,stopOldServer=False):
        
        if stopOldServer: self.stopOldServer()
             
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:            
            while s.connect_ex(('localhost', 3030)) == 0: 
                print('Waiting for ontology server socket to become free...')
                
        print("Starting ontology server...")
        subprocess.Popen(['java', '-jar', 'lib/fuseki/fuseki-server.jar', '--update','--quiet'])
                
    def stopOldServer(self):
        print('Removing any old ontology servers...')
        for l in ((subprocess.Popen(['ps','-A'], stdout=subprocess.PIPE)).communicate()[0]).splitlines():
            if 'java' in str(l):
                pid = int(l.split(None, 1)[0])
                os.kill(pid, 9)    
                break        

    def load(self, filename='uagent.owl'):
        
        print('Waiting for ontology server...')
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            while subprocess.call(['lib/fuseki/s-update','--service=http://localhost:3030/uagent/update', ''],stdout=subprocess.PIPE,stderr=subprocess.PIPE) != 0: 
                pass        
        
        print('Loading ontology...')
        path = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), filename))
        subprocess.call(['lib/fuseki/s-update','--service=http://localhost:3030/uagent/update', "LOAD <file://{}>".format(path)])
        return self

    def add(self,data):
        subprocess.call(['lib/fuseki/s-update', '--service=http://localhost:3030/uagent/update','{} INSERT DATA  {{ {} }}'.format(self.PREFIX,data)])

    def asStringTriple(self,subject,predicate,string):
        return '{} {} "{}".'.format(subject,predicate,string)

    def add_file_object(self,path,subject,predicate):
        string = ""
        with open(path, 'r') as f:
            string += self.asStringTriple(subject,predicate,'\\n'.join(f.read().splitlines()))
        self.add(string)

    def add_instruction_knowledge(self,ace_output):
        
        print("Adding knowledge to ontology...")
        
        facts,rules,groundRules,newFacts = ace_output
        
        string = ''
        
        for fact in facts:
            if string == '':
                string += 'GRAPH {} {{ [ :asFactString "{}"'.format(self.instructionGraph,fact)
            else:
                string += '; :asFactString "{}"'.format(fact)
        for rule in rules:
            string += '; :asRuleString "{}"'.format(rule)
        for rule in groundRules:
            string += '; :asGroundRuleString "{}"'.format(rule)
        for newFact in newFacts:
            string += '; :asReasonerFactString "{}"'.format(newFact)
        
        self.add(string + '] }} . {} a :Instruction .'.format(self.instructionGraph))
        
        # self.add_string(':asFactString',aceFile/Str)
        # self.add_string(':asFactString',drsFile/Str)
        
        return facts,rules,groundRules,newFacts

    def query(self,query):
        return json.loads(str(subprocess.run(['lib/fuseki/s-query','--service','http://localhost:3030/ontology/query',query],stdout=subprocess.PIPE).stdout.decode('utf-8')))

    def query_select_in_one_graph(self,selectors,expression,graph):
        result = self.query('{} SELECT {} WHERE {{ {} union {{ graph {} {} }} }}'.format(self.PREFIX,' '.join(selectors),expression,graph,expression))
        return set(answer[term]['value'] for term in result['head']['vars'] for answer in result['results']['bindings'])

    def query_count_in_one_graph(self,expression,graph):
        result = self.query('{} SELECT (COUNT(*) AS ?count) WHERE {{ {} union {{ graph {} {} }} }} GROUP BY ?count'.format(self.PREFIX,expression,graph,expression))['results']['bindings']
        return int(result[0]['count']['value']) if len(result) == 1 else 0

    def query_count_predicate_in_one_graph(self,predicate,graph):
        return self.query_count_in_one_graph('{{ ?subject {} ?object }}'.format(predicate),graph)

    def query_count_subject_in_one_graph(self,subject,graph):
        return self.query_count_in_one_graph('{{ {} ?predicate ?object }}'.format(subject),graph)

    def query_count_object_in_one_graph(self,object,graph):
        return self.query_count_in_one_graph('{{ ?subject ?predicate {} }}'.format(object),graph)

    def query_count_subject_predicate_in_one_graph(self,subject,predicate,graph):
        return self.query_count_in_one_graph('{{ {} {} ?object }}'.format(subject,predicate),graph)

    def query_count_subject_object_in_one_graph(self,subject,object,graph):
        return self.query_count_in_one_graph('{{ {} ?predicate {} }}'.format(subject,object),graph)

    def query_count_predicate_object_in_one_graph(self,predicate,object,graph):
        return self.query_count_in_one_graph('{{ ?subject {} {} }}'.format(predicate,object),graph)

    def query_select_object_with_predicate_in_one_graph(self,predicate,graph):
        return self.query_select_in_one_graph(['?object'],'{{ ?subject {} ?object }}'.format(predicate),graph)

    def get_instruction_facts(self):
        return self.query_select_object_with_predicate_in_one_graph(':asFactString',self.instructionGraph)

    def get_instruction_reasoner_facts(self):
        return self.query_select_object_with_predicate_in_one_graph(':asReasonerFactString',self.instructionGraph)

    def get_instruction_rules(self):
        return self.query_select_object_with_predicate_in_one_graph(':asRuleString',self.instructionGraph)

    def get_instruction_ground_rules(self):
        return self.query_select_object_with_predicate_in_one_graph(':asGroundRuleString',self.instructionGraph)

    def get_DRS(self):
        return "".join(self.query_select_object_with_predicate_in_one_graph(":asDRSString",self.instructionGraph))

    def get_ACE(self):
        return "".join(self.query_select_object_with_predicate_in_one_graph(":asACEString",self.instructionGraph))

if __name__ == "__main__":
    print("Starting ontology server...")
    Ontology().load()
    